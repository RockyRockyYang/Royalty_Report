using System;
using Xunit;
using RoyaltyReconciliation.API.Models;
using APIFork.Controllers;

namespace RoyaltyTest
{
    public class UnitTest1
    {
        [Fact]
        // a test that always passes
        public void PassingTest()
        {
            int a = 2, b = 1;
            int sum = a + b;
            Assert.Equal(3, sum);
        }

        [Fact]
        // basic test for HttpGet 
        public void GetTest()
        {
            //Arrange
            //var mockGet = new Mock<>();
            var forkController = new APIFork.Controllers.ForkController();

            //Act
            //Assert
            string expected = "working!";
            var ret = forkController.Get();
            Assert.Equal(expected, ret);
        }

        [Fact]
        // test if the machine can successfully run python code
        public void TestSheetName()
        {
            Assert.Equal(6, 6);
            string argument = "C:/Users/ryang/Downloads/02_February_IMO_Wholesale_Report.xlsx";
            Response pyResponse = ForkController.Run_Cmd("../../PythonScript/get_sheetname.py", argument);
            Response expectedResponse = new Response()
            {
                actionResponse = null,
                content = "February 2018\r\nJanuary 2018\r\n",
                fullPath = null,
                sheetList = null,
                success = true
            };
            Assert.Equal(pyResponse.actionResponse, expectedResponse.actionResponse);
            Assert.Equal(pyResponse.content, expectedResponse.content);
            Assert.Equal(pyResponse.fullPath, expectedResponse.fullPath);
            Assert.Equal(pyResponse.sheetList, expectedResponse.sheetList);
            Assert.Equal(pyResponse.success, expectedResponse.success);


            //Assert.Equal<Response>(expectedResponse, pyResponse);
        }

    }
}
