export type ID = string;

export type ISODateString = string; // e.g. "2026-02-05T12:34:56Z"

export type Paginated<T> = {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
};

export type ApiSuccess<T> = {
  data: T;
};

export type ApiError = {
  message: string;
  code?: string;
  details?: unknown;
};
