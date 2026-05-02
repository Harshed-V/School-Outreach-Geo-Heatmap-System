import React from "react";
import { X } from "lucide-react";

const Sheet = ({ open, onOpenChange, children }) => {
  return (
    <>
      {open && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-40" onClick={() => onOpenChange(false)} />
      )}
    </>
  );
};

const SheetContent = React.forwardRef(
  ({ side = "left", className, children, onClose }, ref) => {
    const sideClasses = {
      left: "left-0 top-0 h-full w-[88vw] max-w-[340px] border-r translate-x-0",
      right: "right-0 top-0 h-full w-[88vw] max-w-[340px] border-l translate-x-0",
    };

    return (
      <div
        ref={ref}
        className={`fixed z-50 gap-4 bg-white p-4 shadow-lg transition ease-in-out data-[state=open]:animate-in data-[state=closed]:animate-out ${
          sideClasses[side] || sideClasses.left
        } ${className || ""}`}
      >
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100 transition"
        >
          <X className="h-4 w-4" />
        </button>
        <div className="pt-8">{children}</div>
      </div>
    );
  }
);

SheetContent.displayName = "SheetContent";

export { Sheet, SheetContent };

