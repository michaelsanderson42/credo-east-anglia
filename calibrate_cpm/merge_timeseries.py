import os
import sys
import glob
import getpass
import iris


def make_intermediate_filenames(datadir, var_name, year_start, year_end, monstart, monend):
    '''
    Constructs the filenames containing the bias-corrected data, which are stored in
    one file per month.
    '''

    if monstart > monend:
    # Assume model runs are December to November
        months = [12]
        months.extend(list(range(1, 12)))
    else:
        months = list(range(monstart, monend+1))

    filenames = []
    for m in months:
        month = '{:02d}'.format(m)
        if monstart > monend and m == 12:
            yfirst = year_start
            ylast = '{:04d}'.format(int(year_end)-1)
        else:
            yfirst = '{:04d}'.format(int(year_start)+1)
            ylast = year_end

        filename = f'scaled_distribution_mapping_{var_name}_scenario-0_{yfirst}-{ylast}_month-{month}.nc'
        filenames.append(os.path.join(datadir, filename))

    return filenames


def merge_bias_corrected_files(user_id, project_name, area_name, var_name, ID,
    year_start, year_end, monstart=12, monend=11):

    dir_in = f'/scratch/{user_id}/{project_name}/cpm_calibrated/intermediate/{ID}'

    filenames = make_intermediate_filenames(dir_in, var_name, year_start, year_end, monstart, monend)

    clist = iris.load(filenames)
    cout = iris.cube.CubeList()

    yfirst = int(year_start)
    ylast = int(year_end)

    for y in list(range(yfirst, ylast+1)):
        ycon = iris.Constraint(time = lambda t: t.point.year == y)
        cube_1y = clist.extract(ycon)
        cout.append(cube_1y.concatenate_cube())

    cube = cout.concatenate_cube()

    # Output directory
    dout = f'/scratch/{user_id}/{project_name}/cpm_calibrated/merged/{ID}/{var_name}/'
# If directory doesn't exist, create it.
    try:
        os.makedirs(dout)
    except FileExistsError:
# directory already exists
        pass

    fout = f'{area_name}_{var_name}_rcp85_calib_uk_2.2km_{ID}_{year_start}{monstart:02d}01-{year_end}{monend:02d}30.nc'
    iris.save(cube, os.path.join(dout, fout))


def main():

    user_id = getpass.getuser()
    project_name = sys.argv[1]
    area_name = sys.argv[2]
    var_name = sys.argv[3]
    ID = sys.argv[4]
    year_start = sys.argv[5]
    year_end = sys.argv[6]

    print(user_id, var_name, ID, year_start, year_end)

    merge_bias_corrected_files(user_id, project_name, area_name, var_name, ID, year_start, year_end)


if __name__ == '__main__':
    main()
