This is the codebase for CSCE 678 P0:

TO-DO:
	- Part 2 of P0:
		+ Implement support for 'aggiestack admin show hardware' and 'aggiestack admin can host <hdware> <flavor>'
			- One way this can be done is by storing instances in a separate instance file
			- We could store each instance on a separate line in plain text (This is probably the easiest option)
			- The 'show hardware' command could store all of the servers defined in our server log, and then 
			decrement the memory, disks, and vcpus from the max defined and then output the remaining amount for each server
			' The 'can host' command would do a similar thing, but for a specific server. It would then compare
			the remainder to the flavor and output yes or no.


			- Another way (May be a little more difficult but more efficient):
				+ Decrement the amount of mem, disks, and vcpus for a server in the log. 
				+ Show hardware can then simply iterate through the log and output everything since it's already up to date.
				+ Can host would then just compare the values associated with a server in the hardware log with the specs
				of the flavor entered. 
				+ We could just have additional attributes for each server in the log of:
									<remaining-mem> <remaining-disk> <remaining-vcpus>


File explanations:

aggiestack.py: Where most of the input parsing gets done. 
read_files.py: This is where input files get read, and where log file data is accessed via the show command.

logs/ is the directory where the general hardware, flavor, image log files are stored. As new input files are read,
data gets appended to these logs. 

aggiestack-log.txt: Everytime aggiestack is ran, the command used and whether it succeeded or failed is appended 
to the log. This is all handled in aggiestack.py. 
