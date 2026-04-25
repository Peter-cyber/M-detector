#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

frames="${FRAMES:-40}"
points_per_frame="${POINTS_PER_FRAME:-30000}"
threads_list="${THREADS_LIST:-1 4}"
bag_rate="${BAG_RATE:-1}"
startup_sleep="${STARTUP_SLEEP:-8}"
drain_sleep="${DRAIN_SLEEP:-10}"
result_dir="${RESULT_DIR:-/tmp/m_detector_perf_$(date +%s)}"
if [[ -n "${BAG_FILE:-}" ]]; then
  bag_file="${BAG_FILE}"
else
  bag_file="${result_dir}/synthetic_${frames}x${points_per_frame}.bag"
fi

mkdir -p "${result_dir}"

if [[ -n "${BAG_FILE:-}" ]]; then
  if [[ ! -f "${bag_file}" ]]; then
    echo "BAG_FILE does not exist: ${bag_file}" >&2
    exit 1
  fi
else
  python3 "${repo_dir}/test/perf/make_synthetic_bag.py" \
    --output "${bag_file}" \
    --frames "${frames}" \
    --points-per-frame "${points_per_frame}"
fi

run_index=0
for threads in ${threads_list}; do
  port=$((11311 + run_index))
  run_index=$((run_index + 1))
  export ROS_MASTER_URI="http://localhost:${port}"

  time_file="${result_dir}/time_threads_${threads}.txt"
  launch_log="${result_dir}/dynfilter_threads_${threads}.log"
  play_log="${result_dir}/rosbag_threads_${threads}.log"
  roscore_log="${result_dir}/roscore_threads_${threads}.log"
  rm -f "${time_file}" "${launch_log}" "${play_log}" "${roscore_log}"

  roscore -p "${port}" >"${roscore_log}" 2>&1 &
  roscore_pid=$!
  sleep 2

  export OMP_NUM_THREADS="${threads}"
  roslaunch --wait m_detector detector_kitti.launch rviz:=false time_file:="${time_file}" >"${launch_log}" 2>&1 &
  launch_pid=$!

  sleep "${startup_sleep}"
  rosbag play --quiet -r "${bag_rate}" "${bag_file}" >"${play_log}" 2>&1
  sleep "${drain_sleep}"

  kill -INT "${launch_pid}" >/dev/null 2>&1 || true
  wait "${launch_pid}" >/dev/null 2>&1 || true
  kill -INT "${roscore_pid}" >/dev/null 2>&1 || true
  wait "${roscore_pid}" >/dev/null 2>&1 || true

  python3 "${repo_dir}/test/perf/summarize_time_file.py" "${time_file}" --label "threads=${threads}"
done

echo "result_dir=${result_dir}"
