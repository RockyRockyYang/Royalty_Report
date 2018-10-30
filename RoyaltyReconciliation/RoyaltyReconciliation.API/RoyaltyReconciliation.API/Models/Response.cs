using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace RoyaltyReconciliation.API.Models
{
    public class Response
    {
        public string content { get; set; }
        public IEnumerable<string> sheetList { get; set; }
        public string fullPath { get; set; }
        public ActionResult actionResponse { get; set; }
        public Boolean success { get; set; }
    }
}
