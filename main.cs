using System;
using System.Diagnostics;
using System.Windows.Forms;
using System.IO;

public class main {
    public static void Main(string[] args) {
        DialogResult d = MessageBox.Show("Welcome to Large File Finder Setup by Enderbyte Programs. \nWould you like to install this software on your system?\n\nYes: Install LFF on your computer\nNo: Copy standalone EXE to Downloads Folder\nCancel: Do nothing","Large File Finder Setup",MessageBoxButtons.YesNoCancel,MessageBoxIcon.Question);
        if (d == DialogResult.Yes) {
            //Install System
            System.Diagnostics.Process process = new System.Diagnostics.Process();
            System.Diagnostics.ProcessStartInfo startInfo = new System.Diagnostics.ProcessStartInfo();
            //startInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
            startInfo.FileName = "setup.exe";
            process.StartInfo = startInfo;
            process.Start();
        } else if (d == DialogResult.No) {
            if (File.Exists(System.Environment.ExpandEnvironmentVariables("%USERPROFILE%\\Downloads\\largefilefinder.exe"))) {
                File.Delete(System.Environment.ExpandEnvironmentVariables("%USERPROFILE%\\Downloads\\largefilefinder.exe"));//HAHA
            }
            File.Copy("largefilefinder.exe",System.Environment.ExpandEnvironmentVariables("%USERPROFILE%\\Downloads\\largefilefinder.exe"));
            MessageBox.Show("Copied EXE to "+System.Environment.ExpandEnvironmentVariables("%USERPROFILE%\\Downloads\\largefilefinder.exe"),"Complete",MessageBoxButtons.OK,MessageBoxIcon.Information);
        }
        //Else, quit with no remarks
    }
}