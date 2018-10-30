import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';

import { ImoHeaderModule, ImoTabModule } from '@imo/ng-ui';
import { LoggingInterceptorService } from './logging-interceptor.service';



@NgModule({
  declarations: [
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    ImoHeaderModule,
    ImoTabModule
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: LoggingInterceptorService,
      multi: true
    }
    
  ],
    exports: [
        ImoHeaderModule,
        ImoTabModule
    ]
})
export class CoreModule { }