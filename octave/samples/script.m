#!/usr/bin/octave -qf

printf ("Running octave program: %s", program_name ());
arg_list = argv ();
for i = 1:nargin
  printf (" --> %s", arg_list{i});
endfor
printf ("\n");


userid = getenv("SC_USER_ID")

fileID = fopen("/tmp/output.txt", "wt")
fprintf(fileID, "hello world\n")
fprintf(fileID, userid)
fclose(fileID)
