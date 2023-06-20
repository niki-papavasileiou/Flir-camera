import os
import PySpin
import matplotlib.pyplot as plt
import sys
import keyboard
import time

global continue_recording
continue_recording = True
current_offset_horizontal = 0 
current_offset_vertical = 0
ax = None 

# Functions for moving lines
def move_lines_left():
    global current_offset_horizontal
    current_offset_horizontal -= 40
    pass

def move_lines_right():
    global current_offset_horizontal
    current_offset_horizontal += 40
    pass

def move_lines_up():
    global current_offset_vertical
    current_offset_vertical -= 40
    pass

def move_lines_down():
    global current_offset_vertical
    current_offset_vertical += 40
    pass


def handle_close(evt):
    """
    This function will close the GUI when close event happens.
    :param evt: Event that occurs when the figure closes.
    :type evt: Event
    """

    global continue_recording
    continue_recording = False

def configure_gain(cam,gainn_user):
    """
     This function configures a custom gain. 

     :param cam: Camera to configure gain for.
     :type cam: CameraPtr
     :return: True if successful, False otherwise.
     :rtype: bool
    """
    global count 
    gainn_user = float(gainn_user)
    print('*** CONFIGURING GAIN ***\n')

    try:
        result = True

        cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        print('Automatic gain disabled...')

        gain_to_set = gainn_user 
        cam.Gain.SetValue(gain_to_set)
        print('Gain set to %s us...\n' % gain_to_set)
        count = 2

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result

def configure_exposure(cam,exp_user):
    """
     This function configures a custom exposure time. Automatic exposure is turned
     off in order to allow for the customization, and then the custom setting is
     applied.

     :param cam: Camera to configure exposure for.
     :type cam: CameraPtr
     :return: True if successful, False otherwise.
     :rtype: bool
    """
    global count 

    exp_user = float(exp_user)
    print('*** CONFIGURING EXPOSURE ***\n')

    try:
        result = True

        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            print('Unable to disable automatic exposure. Aborting...')
            return False

        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        print('Automatic exposure disabled...')

        if cam.ExposureTime.GetAccessMode() != PySpin.RW:
            print('Unable to set exposure time. Aborting...')
            return False

        # Ensure desired exposure time does not exceed the maximum
        exposure_time_to_set = exp_user #500000.0
        exposure_time_to_set = min(cam.ExposureTime.GetMax(), exposure_time_to_set)
        cam.ExposureTime.SetValue(exposure_time_to_set)
        print('Shutter time set to %s us...\n' % exposure_time_to_set)
        count = 3

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result

def reset_gain(cam,info_func):
    """
    This function returns the camera to a normal state by re-enabling automatic exposure.

    :param cam: Camera to reset exposure on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    global count 
    try:
        result = True

        cam.GainAuto.SetValue(PySpin.GainAuto_Continuous)
        print('Automatic gain enabled...')
        count = 4
        info_func()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result

def reset_exposure(cam,info_func):
    """
    This function returns the camera to a normal state by re-enabling automatic exposure.

    :param cam: Camera to reset exposure on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    global count 
    try:
        result = True

        # Turn automatic exposure back on
        #
        # *** NOTES ***
        # Automatic exposure is turned on in order to return the camera to its
        # default state.

        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            print('Unable to enable automatic exposure (node retrieval). Non-fatal error...')
            return False

        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)
        cam.GainAuto.SetValue(PySpin.GainAuto_Continuous)

        print('Automatic exposure enabled...')
        count = 5
        info_func()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result

def acquire_and_display_images(cam, nodemap, nodemap_tldevice):
    """
    This function continuously acquires images from a device and display them in a GUI.
    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :param nodemap_tldevice: Transport layer device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type nodemap_tldevice: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    global continue_recording,count
    count = 1
    import tkinter as tk 
    root = tk.Tk()

    frame = tk.Frame(root)
    frame.pack()

    btn_left = tk.Button(root, text='Left', command=lambda:move_lines_left())
    btn_left.pack(side=tk.LEFT)
    btn_right = tk.Button(root, text='Right', command=lambda:move_lines_right())
    btn_right.pack(side=tk.LEFT)
    btn_up = tk.Button(root, text='Up', command=lambda:move_lines_up())
    btn_up.pack(side=tk.LEFT)
    btn_down = tk.Button(root, text='Down', command=lambda :move_lines_down())
    btn_down.pack(side=tk.LEFT)

    exps = tk.Button(root,text='Settings',command=lambda:settings())
    exps.pack()

    def settings(): 
        def set_exp():
            exp_user = exposure_user.get()
            configure_exposure(cam,exp_user)
            info()
        
        def set_gain():
            nonlocal gain_user
            gainn_user = gain_user.get()
            configure_gain(cam,gainn_user)
            info()
            

        def info():
            global gain_label,exp_label

            text_gain = 'Gain: ' + str(cam.Gain.GetValue())
            text_exp = 'Exposure: ' + str(cam.ExposureTime.GetValue())
            if count == 1:
                gain_label = tk.Label(set,text = text_gain)
                exp_label = tk.Label(set,text = text_exp)
                gain_label.pack()
                exp_label.pack()
            else:
                gain_label.config(text = text_gain)
                exp_label.config(text = text_exp)

        set = tk.Toplevel(root)
        set.geometry('200x300')
        set.title('Settings')
        label_exp = tk.Label(set,text='Enter Exposure value')
        label_exp.pack()
        exposure_user = tk.Entry(set, width =30)
        exposure_user.pack()

        exps = tk.Button(set,text='Set Exposure',command=lambda:set_exp())
        exps.pack()
        exps_auto = tk.Button(set,text='Auto Exposure',command=lambda:reset_exposure(cam,info))
        exps_auto.pack()

        label_gain = tk.Label(set,text='Enter Gain value')
        label_gain.pack()
        gain_user = tk.Entry(set, width =30)
        gain_user.pack()

        gain = tk.Button(set,text='Set Gain',command=lambda:set_gain())
        gain.pack()
        gain = tk.Button(set,text='Auto Gain',command=lambda:reset_gain(cam,info))
        gain.pack()

        info()

    sNodemap = cam.GetTLStreamNodeMap()

    # Change bufferhandling mode to NewestOnly
    node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))
    if not PySpin.IsReadable(node_bufferhandling_mode) or not PySpin.IsWritable(node_bufferhandling_mode):
        print('Unable to set stream buffer handling mode.. Aborting...')
        return False

    # Retrieve entry node from enumeration node
    node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
    if not PySpin.IsReadable(node_newestonly):
        print('Unable to set stream buffer handling mode.. Aborting...')
        return False

    # Retrieve integer value from entry node
    node_newestonly_mode = node_newestonly.GetValue()

    # Set integer value from entry node as new value of enumeration node
    node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

    print('*** IMAGE ACQUISITION ***\n')
    try:
        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsReadable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
            return False

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsReadable(node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
            return False

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        print('Acquisition mode set to continuous...')
        cam.BeginAcquisition()

        print('Acquiring images...')

        device_serial_number = ''
        node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
        if PySpin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print('Device serial number retrieved as %s...' % device_serial_number)

        # Close program
        print('Press enter to close the program..')

        # Figure(1) is default so you can omit this line. Figure(0) will create a new window every time program hits this line
        fig = plt.figure(1)

        # Close the GUI when close event happens
        fig.canvas.mpl_connect('close_event', handle_close)

        # Retrieve and display images
        while(continue_recording):
            try:                
                image_result = cam.GetNextImage(1000)

                #  Ensure image completion
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:                    
                    global current_offset_horizontal , current_offset_vertical
                    # Getting the image data as a numpy array
                    image_data = image_result.GetNDArray()

                    # Draws an image on the current figure
                    plt.imshow(image_data, cmap='gray')
                    plt.scatter(image_data.shape[1]/2 + current_offset_horizontal, image_data.shape[0]/2+ current_offset_vertical, s=1, color='red', marker = '+', linewidths=320)

                    # Interval in plt.pause(interval) determines how fast the images are displayed in a GUI
                    # Interval is in seconds.
                    plt.pause(0.001)

                    # Clear current reference of a figure. This will improve display speed significantly
                    plt.clf()
                    
                    # If user presses enter, close the program
                    if keyboard.is_pressed('ENTER'):
                        print('Program is closing...')
                        
                        # Close figure
                        plt.close('all')             
                        input('Done! Press Enter to exit...')
                        continue_recording=False                        

                #  Release image
                #
                #  *** NOTES ***
                #  Images retrieved directly from the camera (i.e. non-converted
                #  images) need to be released in order to keep from filling the
                #  buffer.
                image_result.Release()

            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False

        cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return True


def run_single_camera(cam):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.
    :param cam: Camera to run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Acquire images
        result &= acquire_and_display_images(cam, nodemap, nodemap_tldevice)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def main():
    """
    Example entry point; notice the volume of data that the logging event handler
    prints out on debug despite the fact that very little really happens in this
    example. Because of this, it may be better to have the logger set to lower
    level in order to provide a more concise, focused log.
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    result = True

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Get current library version
    version = system.GetLibraryVersion()
    print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    print('Number of cameras detected: %d' % num_cameras)

    # Finish if there are no cameras
    if num_cameras == 0:

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('Not enough cameras!')
        input('Done! Press Enter to exit...')
        return False

    # Run example on each camera
    for i, cam in enumerate(cam_list):

        print('Running example for camera %d...' % i)

        result &= run_single_camera(cam)
        print('Camera %d example complete... \n' % i)

    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()

    input('Done! Press Enter to exit...')
    return result


if __name__ == '__main__':
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
