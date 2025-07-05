"""OpenSim export functionality."""

import os
import numpy as np
from typing import Any, TYPE_CHECKING
from loguru import logger

from ..core import OpenSimOutput

if TYPE_CHECKING:
    import opensim as osim
    OPENSIM_AVAILABLE = True
else:
    try:
        import opensim as osim
        OPENSIM_AVAILABLE = True
    except ImportError:
        OPENSIM_AVAILABLE = False
        osim = None  # type: ignore
        logger.warning("OpenSim not available. OpenSim export features will be disabled.")

class OpenSimExporter:
    """Handles exporting trial data to OpenSim formats."""
    
    def __init__(self, trial):
        """Initialize with a trial object."""
        if not OPENSIM_AVAILABLE:
            raise ImportError("OpenSim is required for export functionality")
        self.trial = trial
    
    def to_trc(self, 
               filepath: str,
               output_units: str | None = None,
               rotation: np.ndarray = np.eye(3)
               ):
        """
        Export the marker data to TRC file format used by OpenSim
        """  
        table = osim.TimeSeriesTableVec3()
        markers = list(self.trial.points.trajectories.keys())
        table.setColumnLabels(markers)
        conversion_factor = 1.0
        if output_units is not None and self.trial.points.units != output_units:
            logger.info(f"Output units {output_units} do not match points units {self.trial.points.units}. Converting coordinates.")
            # TODO: Convert coordinates to the desired output units
            
        table.addTableMetaDataString("Units", self.trial.points.units)
        table.addTableMetaDataString("DataRate", str(self.trial.points.rate))
        for frame in range(self.trial.points.first_frame, self.trial.points.last_frame + 1):
            row = []
            for marker_name in markers:
                in_coords = self.trial.points.get_marker_coords(marker_name, frame)
                if in_coords is not None:
                    coords = np.array(rotation @ np.array(in_coords).T).T   # Apply rotation if needed
                    coords = coords * conversion_factor # Convert coordinates if needed
                    row.append(osim.Vec3(coords[0], coords[1], coords[2]))
                else:
                    row.append(osim.Vec3().setToNaN())
            time = self.trial.points.time_from_frame(frame)
            table.appendRow(time, osim.RowVectorVec3(row))
        adapter = osim.TRCFileAdapter()
        # Make sure the directories exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        adapter.write(table, filepath)
        self.trial.link_file('trc', filepath)

    def export_force_platforms(self, 
                               output_dir: str, 
                               applied_bodies: dict[int, str], # Expected to be a dict of {platform_index: body_name} where platform_index is 1-based
                               force_expressed_in_body: str = 'ground',
                               point_expressed_in_body: str = 'ground', 
                               force_identifier: str = r'force%d_v',
                               point_identifier: str = r'force%d_p',
                               torque_identifier: str = r'moment%d_',
                               rotation: np.ndarray = np.eye(3),
                               mot_filename: str | None = None,
                               external_loads_filename: str | None = None,
                               unit_force: str = 'N',
                               unit_position: str = 'm',
                               unit_moment: str = 'Nm',
                               metadata: dict[str, Any] = {}
                               ):
        """
        Export force plate metadata to OpenSim ExternalLoads .xml file and the data to a .mot file.
        
        For now, extract foot contact from .enf files, but in the future use contact 
        """
        ext_loads = osim.ExternalLoads()

        if external_loads_filename is None:
            external_loads_filename = f"{self.trial.name}_fp_setup.xml"
        external_loads_filepath = os.path.join(output_dir, external_loads_filename)
        
        if mot_filename is None:
            mot_filename = f"{self.trial.name}_FP.mot"
        mot_filepath = os.path.join(output_dir, mot_filename)
        mot_labels = []
        mot_table = osim.TimeSeriesTable()
        time_col = self.trial.analogs.time

        data = np.zeros((len(self.trial.force_platforms)*9, len(time_col)))  # 3 forces, 3 moments, 3 center of pressure
        for i, fp in enumerate(self.trial.force_platforms): 
            display_i = i + 1  # For display purposes, OpenSim uses 1-based indexing
            fp_force_identifier = force_identifier % (display_i)
            fp_point_identifier = point_identifier % (display_i)
            fp_torque_identifier = torque_identifier % (display_i)
            mot_labels.extend([fp_force_identifier + coord for coord in 'xyz'])
            mot_labels.extend([fp_point_identifier + coord for coord in 'xyz'])  # This could be precomputed, but having it next to the data makes it clear what order it should be added
            mot_labels.extend([fp_torque_identifier + coord for coord in 'xyz'])
            if display_i not in applied_bodies:
                logger.warning(f"Force platform {display_i} does not have an applied body defined. Skipping.")
                continue
            # Create ExternalForce for each force platform        
            ext_force = osim.ExternalForce()
            ext_force.setName(f'FP{str(display_i)}')
            ext_force.setAppliedToBodyName(applied_bodies[display_i])

            ext_force.setForceExpressedInBodyName(force_expressed_in_body)
            ext_force.setForceIdentifier(fp_force_identifier)

            ext_force.setPointExpressedInBodyName(point_expressed_in_body)
            ext_force.setPointIdentifier(fp_point_identifier)

            ext_force.setTorqueIdentifier(fp_torque_identifier)
            
            ext_force.set_data_source_name(mot_filename) 
            
            ext_loads.cloneAndAppend(ext_force)
            
            # Determine conversion factors for units
            force_conversion_factor, position_conversion_factor, moment_conversion_factor = 1.0, 1.0, 1.0
            if fp.unit_force != unit_force:
                logger.warning(f"Force platform {display_i} force unit {fp.unit_force} does not match output unit {unit_force}. Converting forces.")
                current_units = osim.Units(fp.unit_force)
                force_conversion_factor = current_units.convertTo(osim.Units(unit_force))
            if fp.unit_position != unit_position:
                logger.warning(f"Force platform {display_i} position unit {fp.unit_position} does not match output unit {unit_position}. Converting positions.")
                current_units = osim.Units(fp.unit_position)
                position_conversion_factor = current_units.convertTo(osim.Units(unit_position))
            if fp.unit_moment != unit_moment:
                logger.warning(f"Force platform {display_i} torque unit {fp.unit_moment} does not match output unit {unit_moment}. Converting torques.")
                current_units = osim.Units(fp.unit_moment)
                moment_conversion_factor = current_units.convertTo(osim.Units(unit_moment))
                
            # Rotate the force platform data
            force = np.array(rotation @ np.array(fp.force).T).T * force_conversion_factor * -1.0 # OpenSim expects forces to be in the opposite direction
            cop = np.array(rotation @ np.array(fp.center_of_pressure).T).T * position_conversion_factor 
            free_moment = np.array(rotation @ np.array(fp.free_moment).T).T * moment_conversion_factor * -1.0 # OpenSim expects moments to be in the opposite direction
            
            data[i*9:i*9+3, :] = force.T  # 3 forces
            data[i*9+3:i*9+6, :] = cop.T  # 3 center of pressure
            data[i*9+6:i*9+9, :] = free_moment.T  # 3 moments
            
        for i in range(len(time_col)):
            mot_table.appendRow(time_col[i], osim.RowVector(data[:, i]))

        mot_table.setColumnLabels(mot_labels)

        for key, value in metadata.items():
            mot_table.addTableMetaDataString(key, str(value))

        if 'nRows' not in metadata:
            n_frames = self.trial.force_platforms[0].data.height # Assuming all platforms have the same number of frames
            mot_table.addTableMetaDataString('nRows', str(n_frames))
        if 'nColumns' not in metadata:
            n_columns = len(self.trial.force_platforms) * 9  # 3 forces, 3 moments, 3 center of pressure
            mot_table.addTableMetaDataString('nColumns', str(n_columns))
        adapter = osim.STOFileAdapter()
        adapter.write(mot_table, mot_filepath)
        self.trial.link_file(OpenSimOutput.FP_MOT, mot_filepath)
        ext_loads.setDataFileName(mot_filename)
        ext_loads.printToXML(external_loads_filepath)
        self.trial.link_file(OpenSimOutput.FP_SETUP, external_loads_filepath)

    def run_inverse_kinematics(self, 
                        model_path: str, 
                        trc_path: str | None = None,
                        output_dir: str = '.',
                        start_time: float = 0.0,
                        end_time: float = np.inf, 
                        ik_setup_path: str | None = None
                        ):
        if ik_setup_path is None:
            ik_tool = osim.InverseKinematicsTool()
        else:
            ik_tool = osim.InverseKinematicsTool(os.path.abspath(ik_setup_path))

        ik_tool.setName(self.trial.name)
        model = osim.Model(os.path.abspath(model_path))
        ik_tool.setModel(model)
        ik_tool.setMarkerDataFileName(f"{self.trial.name}.trc" if not trc_path else trc_path)
        ik_results_name = f"{self.trial.name}_ik.mot"
        ik_results_path = os.path.join(output_dir, ik_results_name)
        ik_tool.setOutputMotionFileName(ik_results_path)
        ik_tool.setResultsDir(os.path.abspath(output_dir))
        
        # TODO: Could be pulled from trc
        ik_tool.setStartTime(start_time)
        ik_tool.setEndTime(end_time)
        
        out_ik_setup_path = os.path.join(output_dir, f'{self.trial.name}_ik_setup.xml')
        ik_tool.printToXML(out_ik_setup_path)
        self.trial.link_file(OpenSimOutput.IK_SETUP, out_ik_setup_path)
        ik_tool.run()
        self.trial.link_file(OpenSimOutput.IK, ik_results_path)

    def run_inverse_dynamics(self, 
                        model_path: str, 
                        ik_results_path: str | None = None,
                        output_dir: str = '.',
                        id_setup_path: str | None = None,
                        filter_cutoff: float = -1.0,  # Hz - Default is no filtering
                        external_loads_file: str | None = None,
                        excluded_forces: list[str] | None = None
                        ):
        # TODO: Maintain relative paths for Setup files
        #   - Set paths relative to the trial directory?
        #   - Could always set working directory to the trial directory
        #   - OR print with relative paths and then set the tool to use absolute paths (see MATLAB toolbox)
        if id_setup_path is None:
            id_tool = osim.InverseDynamicsTool()
        else:
            id_tool = osim.InverseDynamicsTool(os.path.abspath(id_setup_path))

        id_tool.setName(self.trial.name)
        # model = osim.Model(os.path.abspath(model_path))
        id_tool.setModelFileName(os.path.abspath(model_path))

        ik_results_path = ik_results_path or self.trial.get_linked_file('ik_results')
        ik_sto = osim.Storage(ik_results_path)
        id_tool.setStartTime(ik_sto.getFirstTime())
        id_tool.setEndTime(ik_sto.getLastTime())
        id_tool.setCoordinatesFileName(ik_results_path)
        
        if filter_cutoff > 0:
            id_tool.setLowpassCutoffFrequency(filter_cutoff)
            
        if external_loads_file is not None:
            # Use the provided external loads file
            id_tool.setExternalLoadsFileName(os.path.abspath(external_loads_file))

        if excluded_forces is not None:
            # Exclude specified forces from the ID analysis
            exclude = osim.ArrayStr()
            for force in excluded_forces:
                exclude.append(force)
            id_tool.setExcludedForces(exclude)

        id_results_name = f"{self.trial.name}_id.sto"
        id_results_path = os.path.join(output_dir, id_results_name)
        id_tool.setOutputGenForceFileName(id_results_name)
        id_tool.setResultsDir(os.path.abspath(output_dir))
        out_id_setup_path = os.path.join(output_dir, f'{self.trial.name}_id_setup.xml')
        id_tool.printToXML(out_id_setup_path)
        self.trial.link_file(OpenSimOutput.ID_SETUP, out_id_setup_path)
        id_tool.run()
        self.trial.link_file(OpenSimOutput.ID, id_results_path)
