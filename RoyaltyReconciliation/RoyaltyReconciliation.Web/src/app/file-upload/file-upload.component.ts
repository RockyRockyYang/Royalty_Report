import { Component, ViewEncapsulation } from '@angular/core';
import { HttpClient, HttpRequest, HttpEventType } from '@angular/common/http'
import { FileReport, Argv } from '../models';

@Component({
  selector: 'imo-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss'],
  encapsulation: ViewEncapsulation.None
})

//====================== upload file class ================================
export class FileUploadComponent {
    public title = 'File Component';
    selectedFile: File;
    public progress: string;
    public message: string;
    private fullPath: string;

    private forkUrl = 'http://localhost:60939/api/fork';
    public  loading = false;
    public  uploading = false;

    sheet_List : string[] = [];

    constructor(private http: HttpClient) { }

    //this function to handle upload event and
    //generate candidate sheets for user to choose
    //Input: upload event
    //Return(related html): 
    //InnerHTML:fileinfo
    //Option List: candidate sheets
    uploadFile(event) {
    this.uploading = true;
    if(event.target.files.length == 0){
      console.log("No File Uploaded")
      return;
    }

    //======print file metadata on the webpage=========
    let info = "";
    for(var i=0; i<event.target.files.length; i++){
      info += "file name is: " + event.srcElement.files[i].name + '<br/>';
      info += "file type is: " + event.srcElement.files[i].type + '<br/>';
      info += "file size is: " + event.srcElement.files[i].size + '<br/>';
      info += "file lastModifiedDate is: " + event.srcElement.files[i].lastModifiedDate;
    }
    document.getElementById("fileinfo")!.innerHTML = info;

    //======send POST request to API with upload=========
    const formData = new FormData();
    for(var i=0; i<event.target.files.length; i++){
      var curr_file = <File>event.target.files[i];
      formData.append(curr_file.name, curr_file);
    }
    const uploadReq = new HttpRequest('POST', 'http://localhost:60939/api/upload', formData, 
      {  reportProgress: true,}
    );
    this.http.request(uploadReq).subscribe(event => {
      console.log(event);
      if (event.type === HttpEventType.UploadProgress){
        this.progress = ('Upload Progress: ' + Math.round(event.loaded / event.total!)*100 + '%');
        console.log(this.progress);
      }
      else if (event.type === HttpEventType.Response){
        this.uploading = false;
        const fileReport = event.body as FileReport;
        this.message = fileReport.actionResponse['value'];
        console.log(`fileReport: ${fileReport.sheetList}`)
        this.fullPath = fileReport.fullPath;
        //================generate sheet===========================
        for(var i=0; i< fileReport.sheetList.length; i++){
          this.sheet_List.push(fileReport.sheetList[i]);
        }
      }
    });
  }

  //This function handle the select sheet event. It takes a user event
  //send the request to API, which runs the corresponding python script
  //to do the comparison. It returns the API response result with looker link and 
  //looker built-in windows shows on the website
  //Input: event
  //Return(related html):
  //Innerhtml: forkResult
  selectSheet(event){
    var curr_sheet = event.target.value;
  //===========send post request to API to run the comparison python code=======================
    this.loading = true;
    const argv:Argv = {
      fullPath: this.fullPath,
      currSheet: curr_sheet
    }
    this.http.post(this.forkUrl, argv).subscribe(event=>{
      this.loading = false;
      console.log(event);
      var res = event as FileReport;
      var forkResponse = "";
      if(res.success){
        forkResponse += "Successfully Processed Excel File!" + "<br/>";
        forkResponse += '<a href="http://dev-lookfpv02.imo-online.com/browse">@Looker</br></a>';
        forkResponse += '<iframe src="http://dev-lookfpv02.imo-online.com/embed/dashboards/34?Error%20Code=&Vendor%20Name=eCW&filter_config=%7B%22Error%20Code%22:%5B%7B%22type%22:%22%3D%22,%22values%22:%5B%7B%22constant%22:%22%22%7D,%7B%7D%5D,%22id%22:4%7D%5D,%22Vendor%20Name%22:%5B%7B%22type%22:%22%3D%22,%22values%22:%5B%7B%22constant%22:%22eCW%22%7D,%7B%7D%5D,%22id%22:5%7D%5D%7allow_login_screen=true" width="1700" height="1500" frameborder="0"></iframe>';
      }
      else{
        forkResponse += "Failed to Process Excel File!" + "<br/>";
        forkResponse += res.content;
      }
      document.getElementById("forkResult")!.innerHTML = forkResponse;
      }
    );
  }
}
