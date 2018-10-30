import { NgModule } from '@angular/core';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { AppRoutingModule } from './app-routing.module';


import { ApplicationInsightsModule, AppInsightsService } from '@markpieszak/ng-application-insights';
import { NavigationEnd, Router } from '@angular/router';

import { AppComponent } from './app.component';
import { CoreModule } from './core/core.module';

import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';

//npm materials
import {MatSelectModule} from '@angular/material/select';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';

import 'rxjs/add/operator/filter';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/distinctUntilChanged';
import { FileUploadComponent } from './file-upload/file-upload.component';
//import { FileUploadService } from './services/file-upload.service';
import { HttpModule } from '@angular/http';

@NgModule({
  declarations: [
    AppComponent,
    FileUploadComponent,
  ],
  imports: [
    NoopAnimationsModule,
    CoreModule,
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    HttpModule,
    MatSelectModule,
    MatProgressSpinnerModule,
    ApplicationInsightsModule.forRoot({
      // Your Application Insights key goes here
      instrumentationKey: ''        })
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { 
  
    constructor(
      private _router: Router,
      private _appInsights: AppInsightsService
    ) {
      // Track all page views in Application Insights
      this._router.events
        .filter((event: any) => event instanceof NavigationEnd)
        .map((event: NavigationEnd) => event.urlAfterRedirects)
        .distinctUntilChanged()
        .subscribe((url: string) => {
          this._appInsights.trackPageView(undefined, url);
        });
    }
  
}