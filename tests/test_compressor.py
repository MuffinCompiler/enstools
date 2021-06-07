from os.path import isfile, join
import pytest

def create_synthetic_dataset(directory):
    """
    Creates three synthetic netcdf datasets (1d,2d,3d) into the provided directory.
    :param directory:
    :return: None
    """
    import numpy as np
    import xarray as xr
    import pandas as pd
    from scipy.ndimage import gaussian_filter
    # Create synthetic datasets
    nx, ny, nz, t = 100, 100, 100, 10
    lons = np.linspace(-180, 180, nx)
    lats = np.linspace(-90, 90, ny)
    lon, lat = np.meshgrid(lons, lats)
    levels = np.array(range(nz))
    for dimension in [1, 2, 3]:
        if dimension == 1:
            data_size = (nx, t)
            var_dimensions = ["x", "time"]
            coord_dimensions = ["x"]
            coord_lon = lons
            coord_lat = lats
        elif dimension == 2:
            data_size = (nx, ny, t)
            var_dimensions = ["x", "y", "time"]
            coord_dimensions = ["x", "y"]
            coord_lon = lon
            coord_lat = lat
        elif dimension == 3:
            data_size = (nx, ny, nz, t)
            var_dimensions = ["x", "y", "z", "time"]
            coord_dimensions = ["x", "y"]
            coord_lon = lon
            coord_lat = lat
        else:
            raise NotImplementedError()

        temp = 15 + 8 * np.random.randn(*data_size)
        temp = gaussian_filter(temp, sigma=5)
        precip = 10 * np.random.rand(*data_size)
        precip = gaussian_filter(precip, sigma=5)

        ds = xr.Dataset(
            {
                "temperature": (var_dimensions, temp),
                "precipitation": (var_dimensions, precip),
            },

            coords={
                "lon": (coord_dimensions, coord_lon),
                "lat": (coord_dimensions, coord_lat),
                "level": ("z", levels),
                "time": pd.date_range("2014-09-06", periods=t),
                "reference_time": pd.Timestamp("2014-09-05"),
            },
        )
        ds_name = "dataset_%iD.nc" % dimension
        ds.to_netcdf(join(directory, ds_name))

def file_size(file_path):
    from pathlib import Path
    return Path(file_path).stat().st_size

folders = None

@pytest.fixture(autouse=True)
def wrapper():
    """
    This code will be executed with all the tests
    :return:
    """
    """
    Creates two temporary directories:
    - Input directory: Will store the synthetic data created for the test
    - Output directory: Will store the compressed synthetic data
    :return: Tempdir, Tempdir
    """
    from enstools.core.tempdir import TempDir
    # Create temporary directory in which we'll put some synthetic datasets
    input_tempdir = TempDir(check_free_space=False)
    output_tempdir = TempDir(check_free_space=False)
    create_synthetic_dataset(input_tempdir.getpath())
    global folders
    folders = [input_tempdir, output_tempdir]

    yield

    input_tempdir.cleanup()
    output_tempdir.cleanup()


def test_dataset_exists():
    input_tempdir, output_tempdir = folders
    tempdir_path = input_tempdir.getpath()

    datasets = ["dataset_%iD.nc" % dimension for dimension in range(1, 4)]
    for ds in datasets:
        assert isfile(join(tempdir_path, ds))

@pytest.mark.script_launch_mode('subprocess')
def test_foo_bar(script_runner):
    ret = script_runner.run('ls')
    assert ret.success

@pytest.mark.script_launch_mode('subprocess')
def test_bash(script_runner):
    input_tempdir, output_tempdir = folders
    tempdir_path = input_tempdir.getpath()
    command = ["ls",tempdir_path]
    ret = script_runner.run(*command)
    assert ret.success


@pytest.mark.script_launch_mode('subprocess')
def test_command_is_available(script_runner):
    command = ["enstools-compressor","-h"]
    ret = script_runner.run(*command)
    assert ret.success

@pytest.mark.script_launch_mode('subprocess')
def test_compress_vanilla(script_runner):
    input_tempdir, output_tempdir = folders
    # Check that the compression without specifying compression parameters works
    datasets = ["dataset_%iD.nc" % dimension for dimension in range(1, 4)]
    for ds in datasets:
        input_path = join(input_tempdir.getpath(), ds)
        output_path = output_tempdir.getpath()
        #command = f"enstools-compressor compress {input_path} -o {output_path}"
        command = ["enstools-compressor","compress",input_path,"-o",output_path]
        ret = script_runner.run(*command)
        assert ret.success

# def test_compress_lossless(self):
#     input_tempdir = self.input_tempdir
#     output_tempdir = self.output_tempdir
#     # Check that compression works when specifying compression = lossless
#     datasets = ["dataset_%iD.nc" % dimension for dimension in range(1, 4)]
#     compression = "lossless"
#     for ds in datasets:
#         input_path = join(input_tempdir.getpath(), ds)
#         output_path = output_tempdir.getpath()
#         command = f"enstools-compressor compress {input_path} -o {output_path} --compression {compression}"
#         return_code = launch_bash_command(command)
#         self.assertFalse(return_code)

# def test_compress_lossy(self):
#     input_tempdir = self.input_tempdir
#     output_tempdir = self.output_tempdir
#     # Check that compression works when specifying compression = lossless
#     datasets = ["dataset_%iD.nc" % dimension for dimension in range(1, 4)]
#     compression = "lossy"
#     for ds in datasets:
#         input_path = join(input_tempdir.getpath(), ds)
#         output_path = output_tempdir.getpath()
#         command = f"enstools-compressor compress {input_path} -o {output_path} --compression {compression}"
#         return_code = launch_bash_command(command)
#         self.assertFalse(return_code)

# def test_compress_sz(self):
#     input_tempdir = self.input_tempdir
#     output_tempdir = self.output_tempdir
#     # Check that compression works when specifying compression = lossy:sz
#     datasets = ["dataset_%iD.nc" % dimension for dimension in range(1, 4)]
#     compression = "lossy:sz"
#     for ds in datasets:
#         input_path = join(input_tempdir.getpath(), ds)
#         output_path = output_tempdir.getpath()
#         command = f"enstools-compressor compress {input_path} -o {output_path} --compression {compression}"
#         return_code = launch_bash_command(command)
#         self.assertFalse(return_code)

# def test_compress_sz_pw_rel(self):
#     input_tempdir = self.input_tempdir
#     output_tempdir = self.output_tempdir
#     # Check that compression works when specifying compression = lossy:sz
#     datasets = ["dataset_%iD.nc" % dimension for dimension in range(1, 4)]
#     compression = "lossy:sz:pw_rel:0.1"
#     for ds in datasets:
#         input_path = join(input_tempdir.getpath(), ds)
#         output_path = output_tempdir.getpath()
#         command = f"enstools-compressor compress {input_path} -o {output_path} --compression {compression}"
#         return_code = launch_bash_command(command)
#         self.assertFalse(return_code)

# def test_compress_zfp_vanilla(self):
#     input_tempdir = self.input_tempdir
#     output_tempdir = self.output_tempdir
#     # Check that compression works when specifying compression = lossy:sz
#     datasets = ["dataset_%iD.nc" % dimension for dimension in range(1, 4)]
#     compression = "lossy:zfp"
#     for ds in datasets:
#         input_path = join(input_tempdir.getpath(), ds)
#         output_path = output_tempdir.getpath()
#         command = f"enstools-compressor compress {input_path} -o {output_path} --compression {compression}"
#         return_code = launch_bash_command(command)
#         self.assertFalse(return_code)

# def test_compress_zfp_rate_1(self):
#     input_tempdir = self.input_tempdir
#     output_tempdir = self.output_tempdir
#     # Check that compression works when specifying compression = lossy:sz
#     datasets = ["dataset_%iD.nc" % dimension for dimension in range(1, 4)]
#     compression = "lossy:zfp:rate:1"
#     for ds in datasets:
#         input_path = join(input_tempdir.getpath(), ds)
#         output_path = output_tempdir.getpath()
#         command = f"enstools-compressor compress {input_path} -o {output_path} --compression {compression}"
#         return_code = launch_bash_command(command)
#         self.assertFalse(return_code)

# def test_compress_json_parameters(self):
#     input_tempdir = self.input_tempdir
#     output_tempdir = self.output_tempdir
#     import json
    
#     datasets = ["dataset_%iD.nc" % dimension for dimension in range(1, 4)]
#     compression_parameters = {"default":"lossless",
#                                 "temperature": "lossy:zfp:rate:3",
#                                 "precipitation": "lossless",
#                                 }
#     json_file_path = input_tempdir.getpath()+"/compression.json"
#     with open(json_file_path, "w") as out_file:
#         json.dump(compression_parameters, out_file)
#     compression = json_file_path
#     for ds in datasets:
#         input_path = join(input_tempdir.getpath(), ds)
#         output_path = output_tempdir.getpath()
#         command = f"enstools-compressor compress {input_path} -o {output_path} --compression {compression}"
#         return_code = launch_bash_command(command)
#         self.assertFalse(return_code)

# def test_compress_yaml_parameters(self):
#     input_tempdir = self.input_tempdir
#     output_tempdir = self.output_tempdir
#     import yaml
    
#     datasets = ["dataset_%iD.nc" % dimension for dimension in range(1, 4)]
#     compression_parameters = {"default":"lossless",
#                                 "temperature": "lossy:zfp:rate:3",
#                                 "precipitation": "lossless",
#                                 }
#     json_file_path = input_tempdir.getpath()+"/compression.yaml"
#     with open(json_file_path, "w") as out_file:
#         yaml.dump(compression_parameters, out_file)
#     compression = json_file_path
#     for ds in datasets:
#         input_path = join(input_tempdir.getpath(), ds)
#         output_path = output_tempdir.getpath()
#         command = f"enstools-compressor compress {input_path} -o {output_path} --compression {compression}"
#         return_code = launch_bash_command(command)
#         self.assertFalse(return_code)



# def test_compress_auto(self):
#     input_tempdir = self.input_tempdir
#     output_tempdir = self.output_tempdir
#     # Check that compression works when specifying compression = lossy:sz
#     datasets = ["dataset_%iD.nc" % dimension for dimension in range(1, 4)]
#     compression = "auto"
#     for ds in datasets:
#         input_path = join(input_tempdir.getpath(), ds)
#         output_path = output_tempdir.getpath()
#         command = f"enstools-compressor compress {input_path} -o {output_path} --compression {compression}"
#         return_code = launch_bash_command(command)
#         self.assertFalse(return_code)

# def test_compress_ratios_lossy(self):
#     input_tempdir = self.input_tempdir
#     output_tempdir = self.output_tempdir
#     # Check that compression works when specifying compression = lossy:sz
#     datasets = ["dataset_%iD.nc" % dimension for dimension in range(1, 4)]
#     compression = "lossy"
#     for ds in datasets:
#         input_path = join(input_tempdir.getpath(), ds)
#         output_path = output_tempdir.getpath()
#         output_file_path = join(output_path, ds)
#         command = f"enstools-compressor compress {input_path} -o {output_path} --compression {compression}"
#         return_code = launch_bash_command(command)
#         self.assertFalse(return_code)
#         initial_size = file_size(input_path)
#         final_size = file_size(output_file_path)
#         self.assertGreater(initial_size, final_size)

# def test_compress_ratios_lossless(self):
#     # Check that compression works when specifying compression = lossy:sz
#     input_tempdir = self.input_tempdir
#     output_tempdir = self.output_tempdir

#     datasets = ["dataset_%iD.nc" % dimension for dimension in range(2, 4)]
#     compression = "lossless"
#     for ds in datasets:
#         input_path = join(input_tempdir.getpath(), ds)
#         output_path = output_tempdir.getpath()
#         output_file_path = join(output_path, ds)
#         command = f"enstools-compressor compress {input_path} -o {output_path} --compression {compression}"
#         return_code = launch_bash_command(command)
#         self.assertFalse(return_code)
#         initial_size = file_size(input_path)
#         final_size = file_size(output_file_path)
#         self.assertGreater(initial_size, final_size)

# #def test_compress_multinode(self):
# #    # Check that compression works when specifying compression = lossy:sz
# #    input_tempdir = self.input_tempdir
# #    output_tempdir = self.output_tempdir

# #    datasets = ["dataset_%iD.nc" % dimension for dimension in range(1, 4)]
# #    compression = "lossless"
# #    for ds in datasets:
# #        input_path = join(input_tempdir.getpath(), ds)
# #        output_path = output_tempdir.getpath()
# #        output_file_path = join(output_path, ds)
# #        command = f"enstools-compressor compress {input_path} -o {output_path} --compression {compression} -N 2"
# #        #return_code = launch_bash_command(command)
# #        self.assertFalse(False)

# def test_filters_availability(self):
#     from enstools.io.encoding import check_all_filters_availability
#     self.assertTrue(check_all_filters_availability())

# def test_blosc_filter_availability(self):
#     from enstools.io.encoding import check_blosc_availability
#     self.assertTrue(check_blosc_availability)

# def test_zfp_filter_availability(self):
#     from enstools.io.encoding import check_zfp_availability
#     self.assertTrue(check_zfp_availability)

# def test_sz_filter_availability(self):
#     from enstools.io.encoding import check_sz_availability
#     self.assertTrue(check_sz_availability)


# if __name__ == '__main__':
#     unittest.main()
