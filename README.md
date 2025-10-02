Build error (???) in node-usb. Noticed while trying to update some
stuff to Node 24.

My setup:

    % node --version
    v24.9.0
	% npm --version
    11.6.1
	
To try it:

1. clone this repo
2. `npm install`
3. `npm run compile`

I get an error:

```
node_modules/usb/dist/webusb/webusb-device.d.ts:5:22 - error TS2720: Class 'WebUSBDevice' incorrectly implements class 'USBDevice'. Did you mean to extend 'USBDevice' and inherit its members as a subclass?
  Property 'manufacturerName' is optional in type 'WebUSBDevice' but required in type 'USBDevice'.

5 export declare class WebUSBDevice implements USBDevice {
```
