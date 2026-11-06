export function getImageUrl(value) {
  if (!value) return '';

  if (typeof value === 'string') {
    const cleanValue = value.trim();
    if (!cleanValue) return '';
    if (cleanValue.startsWith('http://') || cleanValue.startsWith('https://') || cleanValue.startsWith('data:')) {
      return cleanValue;
    }
    return cleanValue;
  }

  if (typeof value === 'object') {
    if (typeof value.url === 'string' && value.url.trim()) {
      return value.url.trim();
    }
    if (typeof value.image === 'string' && value.image.trim()) {
      return value.image.trim();
    }
  }

  return '';
}

export function getInitials(name) {
  if (!name) return 'P';
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || '')
    .join('') || 'P';
}
