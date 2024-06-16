import nibabel as nib
import os
import h5py
from sklearn import linear_model
from scipy import stats
import numpy as np
import json
from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('--novol',
                    action='store_true')
args = parser.parse_args()
print(args.novol)
#path to data
fmripreppath = './fmriprep_temp/fmriprep'
#path to output
prepath = './preprocessed/'
#list of tasks
tasklist = ['Item','Loci','Encode','Retrieve'] #put your tasks here
#list of subjects
subs= [
       'sub-105',
]
#list of sessions
sesslist=['ses-01', 'ses-02', 'ses-03']
# determines whether or not to include vol stuff
which_datatypes = ['L', 'R', 'Vol']
vol_str = ''
if args.novol:
    which_datatypes = ['L', 'R']
    vol_str = '_novol'
for sub in subs:
    print('Processing subject:', sub)
    for sess_ind, sess in enumerate(sesslist):
        print('session:', sess)
        if sess == '':
            sess_prefix = os.path.join(fmripreppath, sub, sess, 'func', sub)
        else:
            sess_prefix = os.path.join(fmripreppath, sub, sess, 'func', sub + '_' + sess)
        tasklist_numruns = [2,2,1,1]
        if sess == 'ses-01':
            tasklist_numruns = [3,3,0,0]
        for task_ind, task in enumerate(tasklist):
            num_runs_of_task = tasklist_numruns[task_ind]+1
            task_prefix = sess_prefix + '_task-' + task
            for run in range(1, num_runs_of_task):
                D = dict()
                for hem in which_datatypes:
                    if hem == 'Vol':
                        # Load all timecourses in the 3d brain mask
                        fname =  task_prefix + f'_run-{run}' + '_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'
                        print('      Loading ', fname)
                        nii_4d = nib.load(fname).get_fdata()
                        mask_fname = task_prefix + f'_run-{run}' + '_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz'
                        mask_3d = nib.load(mask_fname).get_fdata().astype(bool)
                        D[hem] = nii_4d[mask_3d]
                    else:
                        # Load all timecourses for one cortical hemisphere
                        # note the filenames are different in some fMRIprep version (20.2.3)
                        # if this doesn't work, try the one commented out below
                        # fname = task_prefix +'_space-fsaverage6_hemi-'+hem+'_bold.func.gii'
                        fname = task_prefix + f'_run-{run}' + '_space-fsaverage6' + '_hemi-' + hem + '_bold.func.gii'
                        print('      Loading ', fname)
                        gi = nib.load(fname)
                        D[hem] = np.column_stack([gi.darrays[t].data for t in range(len(gi.darrays))])
                # Load confound regressors
                conf = np.genfromtxt(task_prefix + f'_run-{run}' + '_desc-confounds_timeseries.tsv', names=True)
                conf_json = json.load(open(task_prefix + f'_run-{run}' + '_desc-confounds_timeseries.json'))
                # Find first combined compcor regressor
                first_cc = 0
                while True:
                    if conf_json['a_comp_cor_%02d' % first_cc]['Mask'] == 'combined':
                        break
                    first_cc += 1
                reg = np.column_stack((
                    # Motion and motion derivatives
                    conf['trans_x'],
                    conf['trans_x_derivative1'],
                    conf['trans_y'],
                    conf['trans_y_derivative1'],
                    conf['trans_z'],
                    conf['trans_z_derivative1'],
                    conf['rot_x'],
                    conf['rot_x_derivative1'],
                    conf['rot_y'],
                    conf['rot_y_derivative1'],
                    conf['rot_z'],
                    conf['rot_z_derivative1'],
                    conf['framewise_displacement'],
                    # First six compcor components (white matter + CSF signals)
                    conf['a_comp_cor_%02d' % first_cc],
                    conf['a_comp_cor_%02d' % (first_cc+1)],
                    conf['a_comp_cor_%02d' % (first_cc+2)],
                    conf['a_comp_cor_%02d' % (first_cc+3)],
                    conf['a_comp_cor_%02d' % (first_cc+4)],
                    conf['a_comp_cor_%02d' % (first_cc+5)],
                    # Cosine (drift) and motion spikes
                    np.column_stack([conf[k] for k in conf.dtype.names if ('cosine' in k) or ('motion_outlier' in k)])))
                # Remove nans, e.g. from framewise_displacement
                reg = np.nan_to_num(reg)
                print('      Cleaning and zscoring')
                for hem in which_datatypes:
                    # Regress out confounds from data
                    regr = linear_model.LinearRegression()
                    regr.fit(reg, D[hem].T)
                    D[hem] = D[hem] - np.dot(regr.coef_, reg.T) - regr.intercept_[:, np.newaxis]
                    # Note 8% of values on cortical surface are NaNs, and the following will therefore throw an error
                    D[hem] = stats.zscore(D[hem], axis=1)
                # Save hdf5 file
                if sess == '':
                    savepath = os.path.join(prepath, sub + '_' + task + '_run-' + str(run) + vol_str + '.h5')
                else:
                    savepath = os.path.join(prepath, sub + '_' + sess + '_' + task + '_run-' + str(run) + vol_str +'.h5')
                with h5py.File(savepath,'w') as hf:
                    grp = hf.create_group(task)
                    grp.create_dataset('L', data=D['L'])
                    grp.create_dataset('R', data=D['R'])
                    if not args.novol:
                        grp.create_dataset('Vol', data=D['Vol'])
                        grp.create_dataset('reg',data=reg)
                        grp.create_dataset('mask', data=mask_3d)
                print('      saved hdf5 file')