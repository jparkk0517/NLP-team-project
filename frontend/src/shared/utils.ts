let timeout: number;
const debounce = (func: () => void, delay: number) => {
  console.log('debounce', timeout);
  return () => {
    clearTimeout(timeout);
    timeout = setTimeout(func, delay);
  };
};

export { debounce };
