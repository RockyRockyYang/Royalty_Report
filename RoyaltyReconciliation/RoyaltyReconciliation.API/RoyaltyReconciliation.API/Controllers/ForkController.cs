using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using System.IO;
using System.Diagnostics;
using System.Text;
using RoyaltyReconciliation.API.Models;

namespace APIFork.Controllers
{
    [Route("api/[controller]")]
    public class ForkController : Controller
    {
        // GET api/Fork
        [HttpGet]
        // default HttpGet method, does nothing related to the project, only shows the service is running
        public string Get()
        {
            string retval = "working!";
            return retval;
        }

        // GET api/Fork/5
        [HttpGet("{id}")]
        public string Get(int id)
        {
            return "value";
        }

        // POST api/Fork
        [HttpPost]
        /*
            @description: Runs load_xls.py and returns the result of the python program when received a HttpPost request
            @param: Argv input takes in a Argv object recording the file path to the excel file and selected sheet in the excel file
            @return: a Response object that shows if the python program is completed successfully and the message from python
        */
        public Response Post([FromBody]Argv input)
        {
            string argument = input.fullPath + " " + '"' + input.currSheet + '"';

            Response responseMsg = Run_Cmd("../../PythonScript/load_xls.py", argument);
            return responseMsg;
        }

        // PUT api/values/5
        [HttpPut("{id}")]
        public void Put(int id, [FromBody]string value)
        {
        }

        // DELETE api/values/5
        [HttpDelete("{id}")]
        public void Delete(int id)
        {
        }
        /*
            @description: runs a python script and get the result of the python program
            @param: pythonFile is the path to the python script user want to execute
            @param: argument is the argument to the python script the user wants to run
            @return: a Response object that shows if the python program is completed successfully and the message from python
        */
        public static Response Run_Cmd(string pythonFile, string argument)
        {
            // create response object
            Response forkResponse = new Response();
            ProcessStartInfo start = new ProcessStartInfo();

            // assume that the python executable exist in C:/Python36/python.exe
            start.FileName = "C:/Python36/python.exe";
            // handle the case for empty argument
            if (argument == "")
            {
                start.Arguments = pythonFile;
            }
            else
            {
                start.Arguments = string.Format("{0} {1}", pythonFile, argument);
            }

            // prepare the response strings of stdout and stderr from python
            start.UseShellExecute = false;
            start.RedirectStandardOutput = true;
            start.RedirectStandardError = true;
            string result = "";
            string errorStr = "";

            // runs the program and receive the inputs fro, the python script
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
            forkResponse.content = result + errorStr;

            // determine if the python program succeeded by checking if there is stderr
            if(errorStr == "")
            {
                forkResponse.success = true;
            }
            else
            {
                forkResponse.success = false;
            }
            return forkResponse;
        }
    }
}
