args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 6) {
  stop("Usage: Rscript spThin-R/scripts/run_r_reference.R <input_csv> <output_json> <thin_par_km> <reps> <long_col> <lat_col> [seed]")
}

input_csv <- args[[1]]
output_json <- args[[2]]
thin_par <- as.numeric(args[[3]])
reps <- as.integer(args[[4]])
long_col <- args[[5]]
lat_col <- args[[6]]
seed <- if (length(args) >= 7) as.integer(args[[7]]) else 123L

haversine_km <- function(lon1, lat1, lon2, lat2) {
  earth_radius_km <- 6371.0088
  lon1_rad <- lon1 * pi / 180
  lat1_rad <- lat1 * pi / 180
  lon2_rad <- lon2 * pi / 180
  lat2_rad <- lat2 * pi / 180

  delta_lon <- lon2_rad - lon1_rad
  delta_lat <- lat2_rad - lat1_rad
  sin_lat <- sin(delta_lat / 2)
  sin_lon <- sin(delta_lon / 2)
  a <- sin_lat ^ 2 + cos(lat1_rad) * cos(lat2_rad) * sin_lon ^ 2
  c <- 2 * asin(pmin(1, sqrt(a)))
  earth_radius_km * c
}

build_conflicts <- function(rec_df, thin_par_km) {
  n <- nrow(rec_df)
  mat <- matrix(FALSE, nrow = n, ncol = n)
  if (n <= 1) {
    return(mat)
  }

  for (i in seq_len(n - 1)) {
    for (j in seq.int(i + 1, n)) {
      dist_km <- haversine_km(rec_df[i, 1], rec_df[i, 2], rec_df[j, 1], rec_df[j, 2])
      if (!is.na(dist_km) && dist_km < thin_par_km) {
        mat[i, j] <- TRUE
        mat[j, i] <- TRUE
      }
    }
  }

  mat
}

thin_algorithm <- function(rec_df_orig, thin_par_km, reps_n) {
  reduced_rec_dfs <- vector("list", reps_n)
  dist_mat_save <- build_conflicts(rec_df_orig, thin_par_km)
  diag(dist_mat_save) <- FALSE
  dist_mat_save[is.na(dist_mat_save)] <- FALSE
  sum_vec_save <- rowSums(dist_mat_save)
  df_keep_save <- rep(TRUE, length(sum_vec_save))

  for (rep_index in seq_len(reps_n)) {
    dist_mat <- dist_mat_save
    sum_vec <- sum_vec_save
    df_keep <- df_keep_save

    while (any(dist_mat) && sum(df_keep) > 1) {
      remove_rec <- which(sum_vec == max(sum_vec))
      if (length(remove_rec) > 1) {
        remove_rec <- sample(remove_rec, 1)
      }

      sum_vec <- sum_vec - dist_mat[, remove_rec]
      sum_vec[remove_rec] <- 0L
      dist_mat[remove_rec, ] <- FALSE
      dist_mat[, remove_rec] <- FALSE
      df_keep[remove_rec] <- FALSE
    }

    reduced_rec_dfs[[rep_index]] <- rec_df_orig[df_keep, , drop = FALSE]
  }

  reduced_rec_order <- order(unlist(lapply(reduced_rec_dfs, nrow)), decreasing = TRUE)
  reduced_rec_dfs[reduced_rec_order]
}

set.seed(seed)
locs_df <- read.csv(input_csv, stringsAsFactors = FALSE)
locs_long_lat <- data.frame(locs_df[[long_col]], locs_df[[lat_col]])

locs_thinned <- thin_algorithm(locs_long_lat, thin_par, reps)
retained_counts <- unlist(lapply(locs_thinned, nrow))
max_retained <- max(retained_counts)
n_max <- sum(retained_counts == max_retained)

json <- sprintf(
  "{\"retained_counts\":[%s],\"max_retained_count\":%d,\"n_max_replicates\":%d}",
  paste(retained_counts, collapse = ","),
  max_retained,
  n_max
)

writeLines(json, output_json)
