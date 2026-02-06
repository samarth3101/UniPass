"use client";

import { useEffect, useRef } from "react";
import { BrowserQRCodeReader } from "@zxing/browser";

type Props = {
  onScan: (text: string) => void;
};

export default function QRScanner({ onScan }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const reader = new BrowserQRCodeReader();
    let controls: any;

    reader.decodeFromVideoDevice(
      undefined,
      videoRef.current!,
      (result) => {
        if (result) {
          onScan(result.getText());
        }
      }
    ).then((result) => {
      controls = result;
    });

    return () => {
      if (controls) {
        controls.stop();
      }
    };
  }, [onScan]);

  return (
    <video
      ref={videoRef}
      className="qr-video"
    />
  );
}
