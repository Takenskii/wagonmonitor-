/** Tracking API — assign / remove / move. */
import { apiRequest } from './client';

export interface AssignRequest {
  wagon_numbers: string[];
  group_id?: string | null;
  new_group_name?: string | null;
  initial_territory?: string | null;
  remove_on_route_end?: boolean;
  deferred_start_at?: string | null;
  auto_remove_at?: string | null;
}

export interface AssignResponse {
  assigned: string[];
  group_id: string | null;
}

export interface RemoveResponse {
  removed: string[];
  not_found: string[];
}

export interface MoveResponse {
  moved: string[];
  group_id: string | null;
}

export const trackingApi = {
  assign: (data: AssignRequest) =>
    apiRequest<AssignResponse>('/tracking/assign/', { method: 'POST', body: data }),

  remove: (wagon_numbers: string[]) =>
    apiRequest<RemoveResponse>('/tracking/remove/', {
      method: 'POST',
      body: { wagon_numbers },
    }),

  move: (data: {
    wagon_numbers: string[];
    group_id?: string | null;
    new_group_name?: string | null;
  }) => apiRequest<MoveResponse>('/tracking/move/', { method: 'POST', body: data }),
};
