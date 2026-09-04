export const navItemClassName = (isActive: boolean) =>
  `${
    isActive
      ? 'border-orange translate-x-2 rounded-l-lg border-r-4 bg-gray-100 text-black'
      : 'rounded-lg text-gray-600 hover:bg-gray-100'
  } flex w-full items-center p-4 text-sm font-medium transition-all duration-200`
