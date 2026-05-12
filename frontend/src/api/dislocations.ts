/** Dislocation API — список вагонов на слежении. */
import { apiRequest } from './client';

export interface WagonDislocation {
  // Идентификаторы (всегда есть — из tracking_assignment)
  track_id: string;
  number: string;

  // Tracking
  group_id: string | null;
  group_name: string | null;
  active: boolean;
  removed_at: string | null;

  // Wagon-инфа (null если вагон ещё не пришёл через ingestion)
  wagon_id: string | null;
  first_seen: string | null;
  last_seen: string | null;
  last_source: string | null;

  // Состояние
  is_full_name: string | null;
  doc_number: string | null;

  // Loading
  loading_date: string | null;
  loading_station: string | null;
  loading_station_name: string | null;
  loading_rw_name: string | null;
  loading_country_name: string | null;

  // Dislocation
  disl_rw: string | null;
  disl_rw_name: string | null;
  disl_country_name: string | null;

  // Operation
  oper_station: string | null;
  oper_station_name: string | null;
  oper_station_department: string | null;
  oper_code: string | null;
  oper_name: string | null;
  oper_full_name: string | null;
  oper_date: string | null;

  // Cargo
  cargo_weight: number | null;
  cargo_code: string | null;
  cargo_name: string | null;
  cargo_full_name: string | null;

  // Train
  train_num: string | null;
  train_index: string | null;
  train_index_1: string | null;
  train_index_2: string | null;
  train_index_3: string | null;
  npp: string | null;
  train_from_station_name: string | null;
  train_to_station_name: string | null;
  car_number: string | null;

  // Destination
  dest_rw: string | null;
  dest_rw_name: string | null;
  dest_country_name: string | null;
  dest_station: string | null;
  dest_station_name: string | null;
  dest_station_department: string | null;
  delivery_date: string | null;
  rest_distance: number | null;
  rest_run: number | null;

  // Recipient / Sender
  grpol_okpo: string | null;
  grpol_name: string | null;
  grpol_rw: string | null;
  grotpr_okpo: string | null;
  grotpr_name: string | null;
  grotpr_rw: string | null;

  // Source
  rash_rw: string | null;
  rash_date: string | null;

  // Station stay
  start_date_on_station: string | null;
  day_count_on_station: number | null;
  days_wo_operation: number | null;
  days_from_start: number | null;
  days_on_trade_union: number | null;
  cl_start_at: string | null;

  // Fault
  faulty_name: string | null;

  // Tech passport
  car_type_name: string | null;
  date_build: string | null;
  capacity: number | null;
  volume: number | null;
  extended_life_time: string | null;
  date_plan_repair: string | null;

  // NSP
  nsp_indicator: string | null;
}

export interface DislocationFilters {
  status?: 'active' | 'archived' | 'all';
  group_id?: string;
  search?: string;
}

export const dislocationsApi = {
  list: (filters: DislocationFilters = {}) => {
    const params = new URLSearchParams();
    if (filters.status) params.set('status', filters.status);
    if (filters.group_id) params.set('group_id', filters.group_id);
    if (filters.search) params.set('search', filters.search);
    const qs = params.toString();
    return apiRequest<WagonDislocation[]>(`/dislocations/${qs ? `?${qs}` : ''}`);
  },
};
