Basic usage:

Somehow get an elevation map as a Numpy binary file - Meshlab can export XYZ points from Unity terrain assets exported as .obj files.
Convert this elevation map into a hazard map:
rosrun policy_server xyzToImage.py <width in px> <points.xyz> <scale>

This produces a hazpackage.pkl file that bundles the original hazmap and the downsampled thresholded versions (corrupted and true) together. In the first step, the points file is saved as a numpy binary file (same prefix, .npy extension) so that subsequent runs are a lot faster

Generate a goal list file, as in launch/goalList.csv. Fields:
1. Goal ID, string
2. Goal X
3. Goal Y

Then, generate the policy package by:
rosrun policy_server <hazPackage.pkl> <goalList.csv>
This produces a complete policy package pickle that has everything wrapped up for the executive

Run the policy executive with:
rosrun policy_server PolicyServer.py _policy:='polpack.pkl'

To look at a policy pickle, use showPolicyFile.py <pol.pkl> 