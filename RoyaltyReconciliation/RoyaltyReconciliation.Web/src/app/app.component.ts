import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'imo-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class AppComponent {
  public title = 'Royalty Report';

  public webConfigSample = `
  ...
  <httpProtocol>
    <customHeaders>
      <add name="Content-Security-Policy-Only" value="object-src 'none'; form-action 'self'; frame-ancestors 'self'" />
      <add name="Content-Security-Policy" value="object-src 'none'; form-action 'self'; frame-ancestors 'self'" />
      <add name="X-Content-Type-Options" value="nosniff" />
      <add name="X-Frame-Options" value="SAMEORIGIN" />
      <add name="Strict-Transport-Security" value="max-age=31536000" />
      <add name="X-XSS-Protection" value="1; mode=block" />
    </customHeaders>
  </httpProtocol>
  ...`;
}
