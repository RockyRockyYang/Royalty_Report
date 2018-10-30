using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using IMO.StatusCheck;
using System.Diagnostics;
using System.IO;

namespace RoyaltyReconciliation.API
{
    public class pythonStatusDependency : IStatusDependency
    {
        public async Task<ValidationState> CheckIfDependencyIsValidAsync()
        {
            //using (var databaseClient = new YourDatabaseClient())
            {
                bool isValid = await CheckPythonStatus();

                return new ValidationState(null, isValid);
            }
        }

        // runs python script to check if python can run successfully and database connection is valid
        // assumes that python is installed at C:/Python36/python.exe
        public async Task<bool> CheckPythonStatus() { 
            string pythonFile = "../../PythonScript/databaseStatus.py";
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = "C:/Python36/python.exe";
            start.Arguments = pythonFile;
            start.UseShellExecute = false;
            start.RedirectStandardOutput = true;
            start.RedirectStandardError = true;
            string result = "";
            string errorStr = "";
            using (Process process = Process.Start(start))
            {
                using (StreamReader reader = process.StandardOutput)
                {
                    result = reader.ReadToEnd();
                }
                using (StreamReader errorReader = process.StandardError)
                {
                    errorStr = errorReader.ReadToEnd();
                }
            }
            result = result + errorStr;
            result = result.Trim();
            if (result == "true")
            {
                return await Task.FromResult(true);
            }
            else {
                return await Task.FromResult(false);
            }

        }

    }
}
