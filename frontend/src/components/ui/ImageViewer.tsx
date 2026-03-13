/**
 * ImageViewer - Vaizdo peržiūros komponentas su zoom, pan, rotate
 * Naudojamas OCR rezultatų palyginimui su originaliu vaizdu
 */

import { useState, useRef, useCallback, useEffect } from "react";
import { Button } from "./button";
import {
  ZoomIn,
  ZoomOut,
  RotateCw,
  RotateCcw,
  Maximize2,
  Move,
  RefreshCw,
} from "lucide-react";

interface ImageViewerProps {
  /** Vaizdo URL arba base64 */
  src: string;
  /** Alt tekstas */
  alt?: string;
  /** Papildoma CSS klasė */
  className?: string;
  /** Ar rodyti kontroles */
  showControls?: boolean;
  /** Pradinis zoom lygis (1 = 100%) */
  initialZoom?: number;
  /** Minimalus zoom */
  minZoom?: number;
  /** Maksimalus zoom */
  maxZoom?: number;
  /** Callback kai pasikeičia zoom */
  onZoomChange?: (zoom: number) => void;
}

interface Position {
  x: number;
  y: number;
}

export function ImageViewer({
  src,
  alt = "Vaizdas",
  className = "",
  showControls = true,
  initialZoom = 1,
  minZoom = 0.25,
  maxZoom = 4,
  onZoomChange,
}: ImageViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  const [zoom, setZoom] = useState(initialZoom);
  const [rotation, setRotation] = useState(0);
  const [position, setPosition] = useState<Position>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState<Position>({ x: 0, y: 0 });
  const [isPanMode, setIsPanMode] = useState(false);

  // Zoom in
  const handleZoomIn = useCallback(() => {
    setZoom((prev) => {
      const newZoom = Math.min(prev * 1.25, maxZoom);
      onZoomChange?.(newZoom);
      return newZoom;
    });
  }, [maxZoom, onZoomChange]);

  // Zoom out
  const handleZoomOut = useCallback(() => {
    setZoom((prev) => {
      const newZoom = Math.max(prev / 1.25, minZoom);
      onZoomChange?.(newZoom);
      return newZoom;
    });
  }, [minZoom, onZoomChange]);

  // Rotate clockwise
  const handleRotateCW = useCallback(() => {
    setRotation((prev) => (prev + 90) % 360);
  }, []);

  // Rotate counter-clockwise
  const handleRotateCCW = useCallback(() => {
    setRotation((prev) => (prev - 90 + 360) % 360);
  }, []);

  // Fit to container
  const handleFitToScreen = useCallback(() => {
    setZoom(1);
    setPosition({ x: 0, y: 0 });
    setRotation(0);
    onZoomChange?.(1);
  }, [onZoomChange]);

  // Reset all
  const handleReset = useCallback(() => {
    setZoom(initialZoom);
    setPosition({ x: 0, y: 0 });
    setRotation(0);
    onZoomChange?.(initialZoom);
  }, [initialZoom, onZoomChange]);

  // Mouse wheel zoom
  const handleWheel = useCallback(
    (e: React.WheelEvent) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      setZoom((prev) => {
        const newZoom = Math.min(Math.max(prev * delta, minZoom), maxZoom);
        onZoomChange?.(newZoom);
        return newZoom;
      });
    },
    [minZoom, maxZoom, onZoomChange]
  );

  // Mouse down - start drag
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (e.button !== 0) return; // Only left click
      setIsDragging(true);
      setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
    },
    [position]
  );

  // Mouse move - drag
  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!isDragging) return;
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    },
    [isDragging, dragStart]
  );

  // Mouse up - end drag
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "+" || e.key === "=") handleZoomIn();
      if (e.key === "-") handleZoomOut();
      if (e.key === "r") handleRotateCW();
      if (e.key === "R") handleRotateCCW();
      if (e.key === "0") handleReset();
      if (e.key === " ") {
        e.preventDefault();
        setIsPanMode((prev) => !prev);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [
    handleZoomIn,
    handleZoomOut,
    handleRotateCW,
    handleRotateCCW,
    handleReset,
  ]);

  return (
    <div className={`relative flex flex-col ${className}`}>
      {/* Controls */}
      {showControls && (
        <div className="flex items-center gap-1 p-2 bg-muted/50 rounded-t-lg border-b">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleZoomOut}
            title="Sumažinti (−)"
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="px-2 text-sm font-medium min-w-[60px] text-center">
            {Math.round(zoom * 100)}%
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleZoomIn}
            title="Padidinti (+)"
          >
            <ZoomIn className="h-4 w-4" />
          </Button>

          <div className="w-px h-6 bg-border mx-1" />

          <Button
            variant="ghost"
            size="sm"
            onClick={handleRotateCCW}
            title="Pasukti kairėn (Shift+R)"
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRotateCW}
            title="Pasukti dešinėn (R)"
          >
            <RotateCw className="h-4 w-4" />
          </Button>

          <div className="w-px h-6 bg-border mx-1" />

          <Button
            variant={isPanMode ? "secondary" : "ghost"}
            size="sm"
            onClick={() => setIsPanMode(!isPanMode)}
            title="Slinkimo režimas (Space)"
          >
            <Move className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleFitToScreen}
            title="Tilpti į ekraną"
          >
            <Maximize2 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleReset}
            title="Atstatyti (0)"
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Image Container */}
      <div
        ref={containerRef}
        className={`relative overflow-hidden bg-muted/30 flex-1 min-h-[300px] ${
          isDragging || isPanMode ? "cursor-grabbing" : "cursor-grab"
        }`}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <div
          className="absolute inset-0 flex items-center justify-center"
          style={{
            transform: `translate(${position.x}px, ${position.y}px)`,
          }}
        >
          <img
            ref={imageRef}
            src={src}
            alt={alt}
            className="max-w-none select-none"
            style={{
              transform: `scale(${zoom}) rotate(${rotation}deg)`,
              transition: isDragging ? "none" : "transform 0.15s ease-out",
            }}
            draggable={false}
          />
        </div>
      </div>

      {/* Rotation indicator */}
      {rotation !== 0 && (
        <div className="absolute bottom-2 right-2 bg-black/50 text-white px-2 py-1 rounded text-xs">
          {rotation}°
        </div>
      )}
    </div>
  );
}

export default ImageViewer;
