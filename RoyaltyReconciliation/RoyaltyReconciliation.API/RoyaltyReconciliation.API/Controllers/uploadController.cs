using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc;
using System.IO;
using System.Diagnostics;
using System.Collections.Generic;
using System.Net.Http.Headers;
using RoyaltyReconciliation.API.Models;
using System;
using System.Linq;

namespace Angular5FileUpload.Controllers
{
    [Produces("application/json")]
    [Route("api/[controller]")]
    public class UploadController : Controller
    {
        private IHostingEnvironment _hostingEnvironment;

        public UploadController(IHostingEnvironment hostingEnvironment)
        {
            _hostingEnvironment = hostingEnvironment;
        }

        [HttpPost, DisableRequestSizeLimit]
        /*
            @description: receive a file stored from front end and store it at backend
            @return: a Response object that shows if the file upload is completed successfully and a list of sheets in excel file
        */
        public Response UploadFile()
        {
            Response responseMsg = new Response();
            // store the file to the //upload folder
            string fullPath = null;
            try
            {
                var file = Request.Form.Files[0];
                string folderName = "Upload";
                string webRootPath = _hostingEnvironment.WebRootPath;
                string newPath = Path.Combine(webRootPath, folderName);
                if (!Directory.Exists(newPath))
                {
                    Directory.CreateDirectory(newPath);
                }
                if (file.Length > 0)
                {
                    string fileName = ContentDispositionHeaderValue.Parse(file.ContentDisposition).FileName.Trim('"');
                    fullPath = Path.Combine(newPath, fileName);
                    using (var stream = new FileStream(fullPath, FileMode.Create))
                    {
                        file.CopyTo(stream);
                    }
                }
                //contains only a single argument snippet, expect to get sheetname
                string result = "";
                IEnumerable<string> sheet_list = null;

                // calls run_cmd function to run python script
                result = Run_Cmd("../../PythonScript/get_sheetname.py", fullPath);
                sheet_list = result.Split("\r\n");
                sheet_list = sheet_list.Take(sheet_list.Count() - 1);
                responseMsg.content = result;
                responseMsg.sheetList = sheet_list;
                responseMsg.fullPath = fullPath;
                responseMsg.actionResponse = Json("Upload Successful!");
                return responseMsg;        
            //return Json("Upload Successful.");
            }
            catch (System.Exception ex)
            {
                responseMsg.actionResponse = Json("Upload Failed: " + ex.Message);
                return responseMsg;
            }
        }

        /*
            @description: runs a python script and get the result of the python program the python returns a list of sheets in the excel
            @param: pythonFile is the path to the python script user want to execute
            @param: argument is the argument to the python script the user wants to run
            @return: a Response object that shows if the python program is completed successfully and the message from python, also contains a list of sheets
        */
        public static String Run_Cmd(string pythonFile, string argument)
        {
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = "C:/Python36/python.exe";
            if (argument == "")
            {
                start.Arguments = pythonFile;
            }
            else
            {
                start.Arguments = string.Format("{0} {1}", pythonFile, argument);
            }
            Console.WriteLine(start.Arguments);
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
            return result + errorStr;
        }

    }
}