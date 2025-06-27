const Api = {
  GET: async <R>(
    url: string,
    params: Record<string, string> = {}
  ): Promise<R> => {
    const queryString = new URLSearchParams(params).toString();
    const response = await fetch(`${url}?${queryString}`, {
      method: 'GET',
    });
    return response.json();
  },
  POST: async <D, R>(url: string, data: D): Promise<R> => {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },
  DELETE: async <R>(url: string): Promise<R> => {
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.json();
  },
};

export { Api };
