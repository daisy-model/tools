'''GUI for prepare_hip_data_for_daisy'''
import os
import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter import ttk
import xarray as xr
import cfunits
from daisy_tools.hip import prepare_hip_data_for_daisy, DDFPressure

def main():
    '''Entry point'''
    root = tk.Tk()
    app = UI(root)
    app.mainloop()

class UI(ttk.Frame):
    # pylint: disable=too-many-ancestors
    '''Class for all GUI stuff'''
    
    def __init__(self, parent, *args, **kwargs):
        '''
        Parameters
        ----------
        parent : tk.Frame
        '''
        super().__init__(parent, *args, **kwargs)
        parent.title('Prepare HIP files for Daisy')
        parent.geometry('800x600')
        self.grid()

        self.buttons = []
        row_offset = self._setup_path_entries(row_offset=0)
        row_offset = self._setup_coords(row_offset)
        row_offset = self._setup_extra_params(row_offset)
        row_offset = self._setup_status_area(row_offset)
        
        self.buttons.append(ttk.Button(self, text="Run", command=self.run))
        self.buttons.append(ttk.Button(self, text="Quit", command=parent.destroy))

        for i,button in enumerate(self.buttons):
            button.grid(column=0, row=i, padx=5, pady=2, sticky=tk.E)

    def _setup_path_entries(self, row_offset):
        self.path_entries = {
            k : ( ttk.Entry(self, width=80), tk.StringVar() ) for k in
            [ 'hs_model_path', 'gw_potential_path', 'outdir']
        }
        for i, (entry, value) in enumerate(self.path_entries.values()):
            entry.grid(column=1, row=row_offset + i, sticky=tk.W)
            value.set("")
            entry["textvariable"] = value
        self.buttons.append(ttk.Button(self, text="Select hydrostratigraphic model",
                                       command=self._set_hs_model_path))
        self.buttons.append(ttk.Button(self, text="Select groundwater potential",
                                       command=self._set_gw_potential_path))
        self.buttons.append(ttk.Button(self, text="Select out directory", command=self._set_outdir))
        return row_offset + len(self.path_entries)
        
    def _setup_coords(self, row_offset):
        self.coords = {
            k : ( ttk.Entry(self, width=10), tk.DoubleVar() ) for k in ['x', 'y']
        }
        for i, (name, (entry, value)) in enumerate(self.coords.items()):
            entry.grid(column=1, row=row_offset + i, sticky=tk.W)
            value.set(0.0)
            entry["textvariable"] = value
            self.buttons.append(ttk.Label(self, text=f"{name} coordinate"))
        return row_offset + len(self.coords)

    def _setup_extra_params(self, row_offset):
        self.extra_params = {
            'dk_model' : ( ttk.Combobox(self, width=5, values=['auto', 1, 2, 3, 4, 5, 6, 7],
                                        state='readonly'),
                           tk.StringVar() ),
            'unit' : ( ttk.Combobox(self, width=5, values=['cm', 'm'],
                                    state='readonly'),
                       tk.StringVar() ),
            'truncate' : ( ttk.Checkbutton(self, onvalue=True, offvalue=False,
                                           text="Round values to 0 decimals"),
                           tk.BooleanVar() ),
        }
        entry, value = self.extra_params['dk_model']
        entry.grid(column=1, row=row_offset, sticky=tk.W)
        value.set('auto')
        entry["textvariable"] = value
        self.buttons.append(ttk.Label(self, text="DK model"))

        entry, value = self.extra_params['unit']
        entry.grid(column=1, row=row_offset+1, sticky=tk.W)
        value.set('cm')
        entry["textvariable"] = value
        self.buttons.append(ttk.Label(self, text="Unit"))

        entry, value = self.extra_params['truncate']
        entry.grid(column=1, row=row_offset+2, sticky=tk.W)
        value.set(True)
        entry["variable"] = value
        self.buttons.append(ttk.Label(self, text="Truncate"))

        return row_offset + len(self.extra_params)
    
    def _setup_status_area(self, row_offset):
        rowspan = 10
        self.status_area_text = tk.StringVar()
        self.status_area_text.set("")
        status_area = ttk.Label(self)
        status_area.grid(column=1, row=row_offset, rowspan=rowspan, sticky=tk.W)
        status_area["textvariable"] = self.status_area_text
        return row_offset + rowspan
            
    def _set_hs_model_path(self):
        self.path_entries['hs_model_path'][1].set(askopenfilename())

    def _set_gw_potential_path(self):
        self.path_entries['gw_potential_path'][1].set(askopenfilename())

    def _set_outdir(self):
        self.path_entries['outdir'][1].set(askdirectory(mustexist=False))

    def get_paths(self):
        '''Get paths as dict of (path_name, path) pairs'''
        return { name : value.get() for name, (_, value) in self.path_entries.items() }

    def get_coords(self):
        '''Get coords as dict of (coord name, coord) pairs'''
        return { name : value.get() for name, (_, value) in self.coords.items() }

    def get_extra_params(self):
        '''Get extra_params as dict of (param name, param value) pairs'''
        return { name : value.get() for name, (_, value) in self.extra_params.items() }
        
    def check_paths(self, paths):
        '''Sanity check paths'''
        errors = []
        if not os.path.exists(paths['hs_model_path']):
            errors.append('Missing hydrostratigraphic model path')
        if not os.path.exists(paths['gw_potential_path']):
            errors.append('Missing groundwater potential path')
        if os.path.exists(paths['outdir']) and not os.path.isdir(paths['outdir']):
            errors.append('Output directory exists and is not a directory')
        return errors

    def check_coords(self, coords):
        '''Sanity check coords'''
        errors = []
        if 'x' not in coords:
            errors.append('Missing x coordinate')
        if 'y' not in coords:
            errors.append('Missing y coordinate')
        return errors
    
    def status_message(self, text):
        '''Display a status message in the status area'''
        self.status_area_text.set(text)
        
    def run(self):
        '''Get parameters from UI, check them and pass to run_prepare_hip_fata_for_daisy'''
        self.status_message('Running')
        try:
            paths = self.get_paths()
            path_errors = self.check_paths(paths)
            if len(path_errors) > 0:
                raise RuntimeError('\n'.join(path_errors))

            coords = self.get_coords()
            coords_errors = self.check_coords(coords)
            if len(coords_errors) > 0:
                raise RuntimeError('\n'.join(coords_errors))

            extra_params = self.get_extra_params()

            saved_paths = run_prepare_hip_data_for_daisy(
                **paths,
                **coords,
                **extra_params,
            )
            
            self.status_message('\n'.join(['Success'] + [
                f'Saved "{k}" to "{v}"' for k,v in saved_paths.items()
            ]))
        except Exception as e: # pylint: disable=broad-exception-caught
            self.status_message(f'Error\n{str(e)}')


def run_prepare_hip_data_for_daisy(hs_model_path, gw_potential_path, x, y, outdir, unit, 
                                   dk_model, truncate):
    '''
    Parameters
    ----------
    hs_model_path : str
      Path to HIP hydrostratigraphic model.
    
    gw_potential_path : str
      Path to HIP ground water potential time series
    
    x, y : int
      Values along X and Y dimension.

    outdir : str
      Path to directory to store outputs in
    
    unit : str
      Express values in this unit (must be interpretable by cfunits.Units)

    dk_model : 'auto' or one of [1,2,3,4,5,6,7]
      If 'auto' guess from hs_model_path

    truncate : bool
      If True round values to 0 decimals.

    Returns
    -------
    saved_paths : dict of (name, path) pairs of the saved files
    '''
    # pylint: disable=too-many-arguments
    if outdir is not None:
        os.makedirs(outdir, exist_ok=True)

    unit = cfunits.Units(unit)
    if dk_model == 'auto':
        dk_model = int(os.path.basename(hs_model_path)[2])
    dk_model = f'DK{dk_model}'
    with xr.open_dataset(hs_model_path) as hs_model, \
         xr.open_dataset(gw_potential_path) as gw_potential:
        soil_column, head_elevation = \
            prepare_hip_data_for_daisy(dk_model, hs_model, gw_potential, x, y, unit)

    if truncate:
        head_elevation['head_elevation'] = head_elevation['head_elevation'].round(0).astype(int)
        cols = ['terrain_height', 'elevation', 'thickness']
        soil_column[cols] = soil_column[cols].round(0).astype(int)

    paths = {
             'Soil column' : os.path.join(outdir, 'soil_column.csv'),
             'Pressure' : os.path.join(outdir, 'pressure.csv'),
             'DDF Pressure' : os.path.join(outdir, 'pressure_table.ddf'),
             'Top aquitard' : os.path.join(outdir, 'top_aquitard.csv')
    }
    soil_column.to_csv(paths['Soil column'], index=False)
    head_elevation.to_csv(paths['Pressure'], index=False)
    DDFPressure(head_elevation).save(paths['DDF Pressure'])
    top_aquitard = soil_column.loc[soil_column['top_aquitard']]
    top_aquitard[
        ['dk_layer', 'elevation', 'thickness', 'unit', 'conductive_properties']
    ].to_csv(paths['Top aquitard'], index=False)
    return paths



if __name__ == '__main__':
    main()
