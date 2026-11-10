/**
 * Input and file validation helpers.
 */

const ALLOWED_IMAGE_TYPES = [
  'image/jpeg',
  'image/png',
  'image/webp'
];

const MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024; // 15MB

export function validateImageFile(file) {
  if (!file) {
    return { valid: false, error: 'No file selected.' };
  }

  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    return {
      valid: false,
      error: `Invalid file type (${file.type}). Only JPEG, PNG, and WebP are supported.`
    };
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    return {
      valid: false,
      error: `File size exceeds 15MB limit (${(file.size / (1024 * 1024)).toFixed(1)}MB).`
    };
  }

  return { valid: true };
}

export function validateBoundingBox(box) {
  if (!box) return false;
  const { xmin, ymin, xmax, ymax } = box;
  return (
    typeof xmin === 'number' &&
    typeof ymin === 'number' &&
    typeof xmax === 'number' &&
    typeof ymax === 'number' &&
    xmin >= 0 &&
    ymin >= 0 &&
    xmax <= 1 &&
    ymax <= 1 &&
    xmax > xmin &&
    ymax > ymin
  );
}

