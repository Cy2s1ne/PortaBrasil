import React from "react";
import { ArrowRight } from "lucide-react";

const InteractiveHoverButton = React.forwardRef(({ text = "Button", icon, className, ...props }, ref) => {
  return (
    <button
      ref={ref}
      {...props}
      className={`group relative inline-flex items-center justify-center px-8 py-3 overflow-hidden rounded-full bg-blue-600 font-medium text-white transition-all duration-300 hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-200 ${className || ""}`}
    >
      <span className="absolute inset-0 flex items-center justify-center transition-all duration-300 opacity-0 group-hover:opacity-100">
        <span className="flex items-center gap-1 transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
          {text}
          {icon || <ArrowRight className="w-4 h-4 ml-1" />}
        </span>
      </span>
      <span className="flex items-center gap-1 group-hover:opacity-0 group-hover:-translate-y-4 transition-all duration-300">
        {text}
        {icon || <ArrowRight className="w-4 h-4 ml-1" />}
      </span>
    </button>
  );
});

InteractiveHoverButton.displayName = "InteractiveHoverButton";

export { InteractiveHoverButton };
