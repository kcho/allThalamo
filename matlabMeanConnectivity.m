function matlabMeanConnectivity()
% print the mean connectivity of thalamus to each cortex
% fileIn is the full path of the img file
% saves the output (appends) to a text file

targetText='~/11/new/totalConnectionProbabilityValuesCON.txt';

files=dir('*');
for i=1:length(files) %grep all folders in pwd
    if (files(i).isdir==1) %if it's folder
        files(i).name %print the file name
        for side={'left','right'} %for left and right side
            for thr={'10','20','30','40','50','60','70','80','90'} %for different levels of thresholds
                directory=strcat(pwd,'/',files(i).name,'/segmentation/with_T1_freesurfer/segmentation/',side,'/',thr,'thrP/');%make up variable called directory which contain all the images
                imgNames=dir(strcat(directory{1},'*seeds*'));%grep image addresses with 'seeds' in it
                
                if length(imgNames)==8 %to make sure there are 8 seeds imgs in the folder
                    sumConnectivity=0;%initial value of the sumConnectivity
                    %looping through files in each images in the directory 

                    %calculating total connectivity to all cortex
                    for imgs = 1:length(imgNames)
                        [path,imgName,ext] = fileparts(imgNames(imgs).name);
                        imgLocation=strcat(directory{1},imgName,ext);
                        %if it is in 'nii.gz'
                        if strcmp(ext,'.gz')==1% if ext is gz
                            system(sprintf('gunzip %s',imgLocation))% gun zip it
                            imgLocation=strcat(imgLocation(1:end-6),'nii');%remove 'nii.gz' and append 'nii' to the file address
                        end
                        
                        subjectName=files(i).name; %getting the folder name as the subject name
                        group=subjectName(1:3);%group name from folder name

                        [z,x,c,modality]=regexp(imgLocation(1:end-4),'[A-Z]{2,4}$');%get cortex part from img name
                        [z,x,c,threshold]=regexp(imgName,'\d*');%get number from img name

                        %fileLocation=strrep(fileLocation,'nii.gz','nii');%change file location to 'nii'

                        %%% actual calculation

                        a=load_nii(imgLocation);% open nii file
                        total=sum(a.img(a.img~=0));% sum of non-zero voxel intensities
                        system(sprintf('gzip %s',imgLocation)) %gzip img
                        eval(sprintf('modality_%s = subs(total)',modality{1}));%each cortex connectivity
                        sumConnectivity=sumConnectivity+total;%accumulate connectivities
                    end 
                    fprintf('Total connectivity is %f',sumConnectivity)
                    
                    %calculating each cortex connectivity divided by the total connectivity
                    imgSequence={'LPFC','LTC','MPFC','MTC','OCC','OFC','PC','SMC'};
                    for total=imgSequence
                        fid=fopen(targetText,'at');
                        eval(sprintf('toPrint = modality_%s/sumConnectivity;',total{1}));
                        fprintf(fid,'%s\t%s\t%s\t%s\t%s\t%.5f\n',subjectName,side{1},group,total{1},threshold{1},toPrint);
                        fclose(fid);
                    end

                end%for each imgs
            end%for many thresholds
        end%for left and right
    end%if it's a folder
end%among all folders
