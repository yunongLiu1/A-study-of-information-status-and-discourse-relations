# A study of information status and discourse relations
 This is a repo is for the python script and executable file for the project.

# Instructions
## To run the executable file
1. Download the executable file app.exe from the repo. [app.exe](href="https://github.com/yunongLiu1/A-study-of-information-status-and-discourse-relations/blob/main/app.zip")
2. Open the command line and navigate to the directory where the app.exe is located.
3. run the executable file with the following command to get the output file with the following name: "full_set_DRels_preposed_constits.txt" in the same directory with the executable file.
```
./app <PATH_TO_PDTB> <PATH_TO_full_set_DRels_preposed_constits>
```


For example:
```
./app ./data/pdtb_v2.0/PDTB-3.0-version2 ./data/decorated_Ss_with_preposed_NP-or-PP_no_blank.txt 
```

OR

run the following command to get the output file with custom name and location:
```
./app <PATH_TO_PDTB> <PATH_TO_decorated_Ss_with_preposed_NP-or-PP_no_blank> <PATH_TO_OUTPUT_FILE>
```

For example:
```
./app ./data/pdtb_v2.0/PDTB-3.0-version2 ./data/decorated_Ss_with_preposed_NP-or-PP_no_blank.txt ./data/output.txt
```

4. The output file will be generated in the same directory as the executable file or the directory specified in the command line.
5. The terminal will print out the number of number of DRel and path of the output file.
<!-- display a image to show the sample output in the terminal -->
![sample output]( /figure/terminal_output.png)





## Sample output file
The output file will be generated in the same directory as the executable file or the directory specified in the command line. The output file will be named "full_set_DRels_preposed_constits.txt" by default or the name specified in the command line. The output file will be in the following format:

![out_file](/figure/sample_output_file.png)
