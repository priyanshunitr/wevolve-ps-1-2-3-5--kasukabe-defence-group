"use client";
import Spline from "@splinetool/react-spline";

export default function SplineBg() {
  return (
    <div className="w-full h-full relative">
      <Spline scene="https://prod.spline.design/eptFcGbRN8-SmKyB/scene.splinecode" />
      <div className="absolute bottom-0 right-0 w-48 h-16 bg-black" />
    </div>
  );
}
