export interface HttpError extends Error {
  statusCode: number;
  code?: string;
}

export const createHttpError = (statusCode: number, message: string, code?: string): HttpError => {
  const error = new Error(message) as HttpError;
  error.statusCode = statusCode;
  if (code) {
    error.code = code;
  }
  return error;
};
