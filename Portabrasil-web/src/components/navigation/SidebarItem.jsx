export default function SidebarItem({ icon, label, isActive, onClick }) {
  const Icon = icon;
  return (
    <div
      onClick={onClick}
      className={`flex items-center px-6 py-4 cursor-pointer transition-colors duration-200 ${
        isActive
          ? 'bg-blue-50 text-blue-600 border-l-4 border-blue-500'
          : 'text-gray-600 hover:bg-gray-50 border-l-4 border-transparent'
      }`}
    >
      <Icon className="w-5 h-5 mr-3" />
      <span className="font-medium text-sm">{label}</span>
    </div>
  );
}
