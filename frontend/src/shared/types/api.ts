export interface ApiMeta {
  request_id: string;
  timestamp: string;
}

export interface ApiSuccessResponse<T> {
  success: true;
  message: string;
  data: T;
  meta: ApiMeta;
}

export interface ApiErrorDetail {
  code: string;
  details: unknown;
}

export interface ApiErrorResponse {
  success: false;
  message: string;
  error: ApiErrorDetail;
  meta: ApiMeta;
}

export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export interface PaginatedData<T> {
  data: T[];
  pagination: PaginationMeta;
}
