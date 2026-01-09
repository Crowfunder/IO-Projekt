// src/utils/imageUtils.js

export const dataURItoBlob = (dataURI) => {
  // Split the base64 string
  const splitDataURI = dataURI.split(',');
  const byteString = splitDataURI[0].indexOf('base64') >= 0 
      ? atob(splitDataURI[1]) 
      : decodeURI(splitDataURI[1]);

  // get the mime component
  const mimeString = splitDataURI[0].split(':')[1].split(';')[0];

  // write the bytes of the string to a typed array
  const ia = new Uint8Array(byteString.length);
  for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
  }

  return new Blob([ia], { type: mimeString });
};