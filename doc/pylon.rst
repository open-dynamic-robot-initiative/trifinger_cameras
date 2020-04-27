*******************
Using Pylon Cameras
*******************

Install Pylon SDK
=================

1. Get the pylon Camera Software Suite (5.0.12) from `here <https://www.baslerweb.com/en/sales-support/downloads/software-downloads/pylon-5-0-12-linux-x86-64-bit/>`_.
   Then follow the instructions in the INSTALL file of the pylon suite. Pasted
   below for reference (2, 3, 4):

2. Change to the directory which contains this INSTALL file, e.g.::

       cd ~/pylon-5.0.0.1234-x86

3. Extract the corresponding SDK into ``/opt``::

       sudo tar -C /opt -xzf pylonSDK*.tar.gz

4. Install udev-rules to set up permissions for basler USB cameras::

       ./setup-usb.sh


Using Pylon in Singularity
==========================

Pylon is currently not installed in the Singularity image so it needs to be
installed on the host system.  To be able to use it from inside Singularity,
the installation path needs to be bound when running the image::

    singularity shell -B /opt/pylon5 blmc_ei.sif

