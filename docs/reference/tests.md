# Справочник тестовых сценариев

Собирается командой `.venv/bin/python scripts/build_documentation.py`. Проверка актуальности — та же команда с `--check`.

Имена отражают проверяемые утверждения; точные fixture и assert приведены в исходном модуле.

<a id="module-tests.test_catalog"></a>

## `test_catalog.py`

Медиаиндекс, очередь и версии превью.

[tests/test_catalog.py](../../tests/test_catalog.py)

<a id="symbol-tests.test_catalog.CatalogTests.test_folder_tree_contains_nested_directories"></a>

### `CatalogTests.test_folder_tree_contains_nested_directories`

```python
def test_folder_tree_contains_nested_directories(self)
```

<a id="symbol-tests.test_catalog.CatalogTests.test_resolve_media_file_returns_scanned_original"></a>

### `CatalogTests.test_resolve_media_file_returns_scanned_original`

```python
def test_resolve_media_file_returns_scanned_original(self)
```

<a id="symbol-tests.test_catalog.CatalogTests.test_resolve_source_folder_stays_inside_source"></a>

### `CatalogTests.test_resolve_source_folder_stays_inside_source`

```python
def test_resolve_source_folder_stays_inside_source(self)
```

<a id="symbol-tests.test_catalog.CatalogTests.test_scan_is_persistent_and_reconciles_removed_entries"></a>

### `CatalogTests.test_scan_is_persistent_and_reconciles_removed_entries`

```python
def test_scan_is_persistent_and_reconciles_removed_entries(self)
```

<a id="symbol-tests.test_catalog.CatalogTests.test_source_role_label_and_comment_can_be_updated"></a>

### `CatalogTests.test_source_role_label_and_comment_can_be_updated`

```python
def test_source_role_label_and_comment_can_be_updated(self)
```

<a id="symbol-tests.test_catalog.CatalogTests.test_system_photos_source_is_virtual_and_groups_assets_by_month"></a>

### `CatalogTests.test_system_photos_source_is_virtual_and_groups_assets_by_month`

```python
def test_system_photos_source_is_virtual_and_groups_assets_by_month(self)
```

<a id="symbol-tests.test_catalog.CatalogTests.test_thumbnail_queue_is_persistent_and_tracks_progress"></a>

### `CatalogTests.test_thumbnail_queue_is_persistent_and_tracks_progress`

```python
def test_thumbnail_queue_is_persistent_and_tracks_progress(self)
```

<a id="module-tests.test_comparison"></a>

## `test_comparison.py`

Общая сверка имён и совместимость отчётов.

[tests/test_comparison.py](../../tests/test_comparison.py)

<a id="symbol-tests.test_comparison.ComparisonTests.test_background_pause_resume_and_single_worker"></a>

### `ComparisonTests.test_background_pause_resume_and_single_worker`

```python
def test_background_pause_resume_and_single_worker(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_complete_lists_are_reused_offline_without_filesystem_access"></a>

### `ComparisonTests.test_complete_lists_are_reused_offline_without_filesystem_access`

```python
def test_complete_lists_are_reused_offline_without_filesystem_access(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_directory_list_cache_is_available_in_explorer_offline"></a>

### `ComparisonTests.test_directory_list_cache_is_available_in_explorer_offline`

```python
def test_directory_list_cache_is_available_in_explorer_offline(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_empty_directories_are_compared_and_file_directory_types_stay_distinct"></a>

### `ComparisonTests.test_empty_directories_are_compared_and_file_directory_types_stay_distinct`

```python
def test_empty_directories_are_compared_and_file_directory_types_stay_distinct(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_incomplete_target_prevents_absence_claim_but_keeps_matches"></a>

### `ComparisonTests.test_incomplete_target_prevents_absence_claim_but_keeps_matches`

```python
def test_incomplete_target_prevents_absence_claim_but_keeps_matches(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_legacy_large_identifiers_still_roundtrip_without_loss"></a>

### `ComparisonTests.test_legacy_large_identifiers_still_roundtrip_without_loss`

```python
def test_legacy_large_identifiers_still_roundtrip_without_loss(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_legacy_resume_creates_name_job_and_preserves_old_report_and_lists"></a>

### `ComparisonTests.test_legacy_resume_creates_name_job_and_preserves_old_report_and_lists`

```python
def test_legacy_resume_creates_name_job_and_preserves_old_report_and_lists(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_name_filter_keeps_ancestors_and_paginates"></a>

### `ComparisonTests.test_name_filter_keeps_ancestors_and_paginates`

```python
def test_name_filter_keeps_ancestors_and_paginates(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_names_match_even_when_content_size_and_parent_location_differ"></a>

### `ComparisonTests.test_names_match_even_when_content_size_and_parent_location_differ`

```python
def test_names_match_even_when_content_size_and_parent_location_differ(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_never_reads_file_contents_or_requests_file_stat"></a>

### `ComparisonTests.test_never_reads_file_contents_or_requests_file_stat`

```python
def test_never_reads_file_contents_or_requests_file_stat(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_offline_source_without_a_complete_list_fails"></a>

### `ComparisonTests.test_offline_source_without_a_complete_list_fails`

```python
def test_offline_source_without_a_complete_list_fails(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_refresh_lists_is_explicit_and_reused_lists_keep_their_dates"></a>

### `ComparisonTests.test_refresh_lists_is_explicit_and_reused_lists_keep_their_dates`

```python
def test_refresh_lists_is_explicit_and_reused_lists_keep_their_dates(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_rejects_overlap_and_traversal_and_checks_mount_identity"></a>

### `ComparisonTests.test_rejects_overlap_and_traversal_and_checks_mount_identity`

```python
def test_rejects_overlap_and_traversal_and_checks_mount_identity(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_restart_leaves_interrupted_job_paused"></a>

### `ComparisonTests.test_restart_leaves_interrupted_job_paused`

```python
def test_restart_leaves_interrupted_job_paused(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_same_content_with_different_name_is_not_a_name_match"></a>

### `ComparisonTests.test_same_content_with_different_name_is_not_a_name_match`

```python
def test_same_content_with_different_name_is_not_a_name_match(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_same_filename_in_other_folder_is_separate_status"></a>

### `ComparisonTests.test_same_filename_in_other_folder_is_separate_status`

```python
def test_same_filename_in_other_folder_is_separate_status(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_same_named_matches_on_two_volumes_expand_independently"></a>

### `ComparisonTests.test_same_named_matches_on_two_volumes_expand_independently`

```python
def test_same_named_matches_on_two_volumes_expand_independently(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_scopes_do_not_reuse_another_directorys_list"></a>

### `ComparisonTests.test_scopes_do_not_reuse_another_directorys_list`

```python
def test_scopes_do_not_reuse_another_directorys_list(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_symlinks_special_files_and_originals_remain_untouched"></a>

### `ComparisonTests.test_symlinks_special_files_and_originals_remain_untouched`

```python
def test_symlinks_special_files_and_originals_remain_untouched(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_target_tree_expands_saved_subdirectories_without_accessing_nas"></a>

### `ComparisonTests.test_target_tree_expands_saved_subdirectories_without_accessing_nas`

```python
def test_target_tree_expands_saved_subdirectories_without_accessing_nas(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_target_tree_only_reads_target_scopes_in_the_requested_job"></a>

### `ComparisonTests.test_target_tree_only_reads_target_scopes_in_the_requested_job`

```python
def test_target_tree_only_reads_target_scopes_in_the_requested_job(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_target_tree_paginates_names_and_does_not_follow_symlinks"></a>

### `ComparisonTests.test_target_tree_paginates_names_and_does_not_follow_symlinks`

```python
def test_target_tree_paginates_names_and_does_not_follow_symlinks(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_two_target_locations_and_directory_matches_are_explained"></a>

### `ComparisonTests.test_two_target_locations_and_directory_matches_are_explained`

```python
def test_two_target_locations_and_directory_matches_are_explained(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_unicode_and_case_names_are_normalized"></a>

### `ComparisonTests.test_unicode_and_case_names_are_normalized`

```python
def test_unicode_and_case_names_are_normalized(self)
```

<a id="symbol-tests.test_comparison.ComparisonTests.test_unreadable_source_branch_is_visible_in_unverified_filter"></a>

### `ComparisonTests.test_unreadable_source_branch_is_visible_in_unverified_filter`

```python
def test_unreadable_source_branch_is_visible_in_unverified_filter(self)
```

<a id="module-tests.test_comparison_tree_ui"></a>

## `test_comparison_tree_ui.py`

Дерево найденных путей и пагинация.

[tests/test_comparison_tree_ui.py](../../tests/test_comparison_tree_ui.py)

<a id="symbol-tests.test_comparison_tree_ui.ComparisonTreeTests.test_identical_paths_on_two_targets_have_independent_folder_pages"></a>

### `ComparisonTreeTests.test_identical_paths_on_two_targets_have_independent_folder_pages`

```python
async def test_identical_paths_on_two_targets_have_independent_folder_pages(self)
```

<a id="symbol-tests.test_comparison_tree_ui.ComparisonTreeTests.test_opened_folder_keeps_matches_and_breadcrumb_navigation_within_its_scope"></a>

### `ComparisonTreeTests.test_opened_folder_keeps_matches_and_breadcrumb_navigation_within_its_scope`

```python
async def test_opened_folder_keeps_matches_and_breadcrumb_navigation_within_its_scope(self)
```

<a id="symbol-tests.test_comparison_tree_ui.ComparisonTreeTests.test_slow_folder_open_cannot_focus_previous_source_results"></a>

### `ComparisonTreeTests.test_slow_folder_open_cannot_focus_previous_source_results`

```python
async def test_slow_folder_open_cannot_focus_previous_source_results(self)
```

<a id="symbol-tests.test_comparison_tree_ui.ComparisonTreeTests.test_slow_folder_response_cannot_restore_results_from_previous_selection"></a>

### `ComparisonTreeTests.test_slow_folder_response_cannot_restore_results_from_previous_selection`

```python
async def test_slow_folder_response_cannot_restore_results_from_previous_selection(self)
```

<a id="module-tests.test_copies"></a>

## `test_copies.py`

Наборы папок, нумерация и пересечения.

[tests/test_copies.py](../../tests/test_copies.py)

<a id="symbol-tests.test_copies.CopyCatalogTests.test_concurrent_registrations_allocate_unique_consecutive_numbers"></a>

### `CopyCatalogTests.test_concurrent_registrations_allocate_unique_consecutive_numbers`

```python
def test_concurrent_registrations_allocate_unique_consecutive_numbers(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_folder_labels_and_tracking_are_independent_and_survive_restart_and_disconnect"></a>

### `CopyCatalogTests.test_folder_labels_and_tracking_are_independent_and_survive_restart_and_disconnect`

```python
def test_folder_labels_and_tracking_are_independent_and_survive_restart_and_disconnect(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_idempotent_registration_does_not_allocate_extra_copy_numbers"></a>

### `CopyCatalogTests.test_idempotent_registration_does_not_allocate_extra_copy_numbers`

```python
def test_idempotent_registration_does_not_allocate_extra_copy_numbers(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_invalid_settings_cannot_modify_a_group_or_create_orphan_records"></a>

### `CopyCatalogTests.test_invalid_settings_cannot_modify_a_group_or_create_orphan_records`

```python
def test_invalid_settings_cannot_modify_a_group_or_create_orphan_records(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_last_deletion_reuses_number_and_ignores_legacy_counter"></a>

### `CopyCatalogTests.test_last_deletion_reuses_number_and_ignores_legacy_counter`

```python
def test_last_deletion_reuses_number_and_ignores_legacy_counter(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_middle_deletion_requires_confirmed_renumbering_before_adding"></a>

### `CopyCatalogTests.test_middle_deletion_requires_confirmed_renumbering_before_adding`

```python
def test_middle_deletion_requires_confirmed_renumbering_before_adding(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_numbers_span_copy_types_and_labels_inherit_with_path_boundaries"></a>

### `CopyCatalogTests.test_numbers_span_copy_types_and_labels_inherit_with_path_boundaries`

```python
def test_numbers_span_copy_types_and_labels_inherit_with_path_boundaries(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_offline_locations_and_changed_mount_names_preserve_relationships_after_restart"></a>

### `CopyCatalogTests.test_offline_locations_and_changed_mount_names_preserve_relationships_after_restart`

```python
def test_offline_locations_and_changed_mount_names_preserve_relationships_after_restart(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_old_catalog_gets_empty_settings_and_deleted_groups_leave_no_settings"></a>

### `CopyCatalogTests.test_old_catalog_gets_empty_settings_and_deleted_groups_leave_no_settings`

```python
def test_old_catalog_gets_empty_settings_and_deleted_groups_leave_no_settings(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_old_volume_roles_do_not_create_main_folders_or_links"></a>

### `CopyCatalogTests.test_old_volume_roles_do_not_create_main_folders_or_links`

```python
def test_old_volume_roles_do_not_create_main_folders_or_links(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_only_tracked_groups_record_changes_and_stale_acknowledgements_preserve_new_changes"></a>

### `CopyCatalogTests.test_only_tracked_groups_record_changes_and_stale_acknowledgements_preserve_new_changes`

```python
def test_only_tracked_groups_record_changes_and_stale_acknowledgements_preserve_new_changes(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_overlapping_roots_cannot_give_descendants_conflicting_labels"></a>

### `CopyCatalogTests.test_overlapping_roots_cannot_give_descendants_conflicting_labels`

```python
def test_overlapping_roots_cannot_give_descendants_conflicting_labels(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_registration_changes_no_files_and_does_not_require_fresh_directory_reads"></a>

### `CopyCatalogTests.test_registration_changes_no_files_and_does_not_require_fresh_directory_reads`

```python
def test_registration_changes_no_files_and_does_not_require_fresh_directory_reads(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_rejects_files_unknown_paths_and_unverified_disks"></a>

### `CopyCatalogTests.test_rejects_files_unknown_paths_and_unverified_disks`

```python
def test_rejects_files_unknown_paths_and_unverified_disks(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_renumbering_compacts_multiple_gaps_atomically_without_changing_files"></a>

### `CopyCatalogTests.test_renumbering_compacts_multiple_gaps_atomically_without_changing_files`

```python
def test_renumbering_compacts_multiple_gaps_atomically_without_changing_files(self)
```

<a id="symbol-tests.test_copies.CopyCatalogTests.test_stale_renumbering_proposal_cannot_change_newer_links_or_types"></a>

### `CopyCatalogTests.test_stale_renumbering_proposal_cannot_change_newer_links_or_types`

```python
def test_stale_renumbering_proposal_cannot_change_newer_links_or_types(self)
```

<a id="module-tests.test_copy_connections"></a>

## `test_copy_connections.py`

Подключение и отключение связей.

[tests/test_copy_connections.py](../../tests/test_copy_connections.py)

<a id="symbol-tests.test_copy_connections.ConnectionActionsTests.test_copying_blocks_disconnect_without_changing_any_state"></a>

### `ConnectionActionsTests.test_copying_blocks_disconnect_without_changing_any_state`

```python
async def test_copying_blocks_disconnect_without_changing_any_state(self)
```

<a id="symbol-tests.test_copy_connections.ConnectionActionsTests.test_disconnect_uses_reversible_api_unlinks_pair_and_opens_section"></a>

### `ConnectionActionsTests.test_disconnect_uses_reversible_api_unlinks_pair_and_opens_section`

```python
async def test_disconnect_uses_reversible_api_unlinks_pair_and_opens_section(self)
```

<a id="symbol-tests.test_copy_connections.CopyConnectionTests.test_api_can_disconnect_and_reconnect_but_will_not_interrupt_copying"></a>

### `CopyConnectionTests.test_api_can_disconnect_and_reconnect_but_will_not_interrupt_copying`

```python
def test_api_can_disconnect_and_reconnect_but_will_not_interrupt_copying(self)
```

<a id="symbol-tests.test_copy_connections.CopyConnectionTests.test_disconnect_removes_roles_from_tree_properties_and_saved_snapshots"></a>

### `CopyConnectionTests.test_disconnect_removes_roles_from_tree_properties_and_saved_snapshots`

```python
def test_disconnect_removes_roles_from_tree_properties_and_saved_snapshots(self)
```

<a id="symbol-tests.test_copy_connections.CopyConnectionTests.test_disconnected_copy_hides_only_its_own_role"></a>

### `CopyConnectionTests.test_disconnected_copy_hides_only_its_own_role`

```python
def test_disconnected_copy_hides_only_its_own_role(self)
```

<a id="symbol-tests.test_copy_connections.CopyConnectionTests.test_disconnected_group_preserves_labels_numbers_and_history_after_restart"></a>

### `CopyConnectionTests.test_disconnected_group_preserves_labels_numbers_and_history_after_restart`

```python
def test_disconnected_group_preserves_labels_numbers_and_history_after_restart(self)
```

<a id="symbol-tests.test_copy_connections.CopyConnectionTests.test_individual_disconnect_survives_whole_group_round_trip_without_renumbering"></a>

### `CopyConnectionTests.test_individual_disconnect_survives_whole_group_round_trip_without_renumbering`

```python
def test_individual_disconnect_survives_whole_group_round_trip_without_renumbering(self)
```

<a id="symbol-tests.test_copy_connections.CopyConnectionTests.test_invalid_connections_and_explicit_deletion"></a>

### `CopyConnectionTests.test_invalid_connections_and_explicit_deletion`

```python
def test_invalid_connections_and_explicit_deletion(self)
```

<a id="symbol-tests.test_copy_connections.CopyConnectionTests.test_missing_disk_keeps_roles_when_relationship_was_not_disabled"></a>

### `CopyConnectionTests.test_missing_disk_keeps_roles_when_relationship_was_not_disabled`

```python
def test_missing_disk_keeps_roles_when_relationship_was_not_disabled(self)
```

<a id="symbol-tests.test_copy_connections.SidebarSectionsTests.test_manual_disconnect_remains_visible_while_unknown_availability_stays_active"></a>

### `SidebarSectionsTests.test_manual_disconnect_remains_visible_while_unknown_availability_stays_active`

```python
def test_manual_disconnect_remains_visible_while_unknown_availability_stays_active(self)
```

<a id="symbol-tests.test_copy_connections.SidebarSectionsTests.test_offline_copy_keeps_its_group_and_online_siblings_visible"></a>

### `SidebarSectionsTests.test_offline_copy_keeps_its_group_and_online_siblings_visible`

```python
def test_offline_copy_keeps_its_group_and_online_siblings_visible(self)
```

<a id="symbol-tests.test_copy_connections.SidebarSectionsTests.test_offline_main_does_not_hide_online_copy_and_all_offline_moves_whole_group"></a>

### `SidebarSectionsTests.test_offline_main_does_not_hide_online_copy_and_all_offline_moves_whole_group`

```python
def test_offline_main_does_not_hide_online_copy_and_all_offline_moves_whole_group(self)
```

<a id="module-tests.test_copy_files"></a>

## `test_copy_files.py`

Планы, запись, гонки и незавершённые копии.

[tests/test_copy_files.py](../../tests/test_copy_files.py)

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_api_preview_and_execution_use_only_the_registered_direction"></a>

### `MissingCopyTests.test_api_preview_and_execution_use_only_the_registered_direction`

```python
def test_api_preview_and_execution_use_only_the_registered_direction(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_changed_source_since_report_is_not_copied"></a>

### `MissingCopyTests.test_changed_source_since_report_is_not_copied`

```python
def test_changed_source_since_report_is_not_copied(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_completed_copy_creates_new_comparison_and_keeps_other_marks_and_old_report"></a>

### `MissingCopyTests.test_completed_copy_creates_new_comparison_and_keeps_other_marks_and_old_report`

```python
def test_completed_copy_creates_new_comparison_and_keeps_other_marks_and_old_report(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_conflicting_parent_and_its_descendants_are_not_in_plan"></a>

### `MissingCopyTests.test_conflicting_parent_and_its_descendants_are_not_in_plan`

```python
def test_conflicting_parent_and_its_descendants_are_not_in_plan(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_existing_target_created_after_preview_is_skipped"></a>

### `MissingCopyTests.test_existing_target_created_after_preview_is_skipped`

```python
def test_existing_target_created_after_preview_is_skipped(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_interrupted_network_copy_is_marked_even_when_its_size_already_matches"></a>

### `MissingCopyTests.test_interrupted_network_copy_is_marked_even_when_its_size_already_matches`

```python
def test_interrupted_network_copy_is_marked_even_when_its_size_already_matches(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_network_copy_uses_exclusive_creation_without_atomic_rename"></a>

### `MissingCopyTests.test_network_copy_uses_exclusive_creation_without_atomic_rename`

```python
def test_network_copy_uses_exclusive_creation_without_atomic_rename(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_network_target_appearing_before_exclusive_open_is_skipped"></a>

### `MissingCopyTests.test_network_target_appearing_before_exclusive_open_is_skipped`

```python
def test_network_target_appearing_before_exclusive_open_is_skipped(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_no_space_fails_without_publishing_a_file"></a>

### `MissingCopyTests.test_no_space_fails_without_publishing_a_file`

```python
def test_no_space_fails_without_publishing_a_file(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_only_missing_files_and_directories_are_created"></a>

### `MissingCopyTests.test_only_missing_files_and_directories_are_created`

```python
def test_only_missing_files_and_directories_are_created(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_parent_replaced_during_copy_is_detected_before_publication"></a>

### `MissingCopyTests.test_parent_replaced_during_copy_is_detected_before_publication`

```python
def test_parent_replaced_during_copy_is_detected_before_publication(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_preview_freezes_fresh_source_metadata_without_reading_file_contents"></a>

### `MissingCopyTests.test_preview_freezes_fresh_source_metadata_without_reading_file_contents`

```python
def test_preview_freezes_fresh_source_metadata_without_reading_file_contents(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_preview_is_readonly_and_requires_a_completed_file_report"></a>

### `MissingCopyTests.test_preview_is_readonly_and_requires_a_completed_file_report`

```python
def test_preview_is_readonly_and_requires_a_completed_file_report(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_registered_aliases_cannot_make_a_nested_copy_inside_the_source"></a>

### `MissingCopyTests.test_registered_aliases_cannot_make_a_nested_copy_inside_the_source`

```python
def test_registered_aliases_cannot_make_a_nested_copy_inside_the_source(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_removed_link_and_offline_volume_cannot_start_a_plan"></a>

### `MissingCopyTests.test_removed_link_and_offline_volume_cannot_start_a_plan`

```python
def test_removed_link_and_offline_volume_cannot_start_a_plan(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_restart_records_interruption_and_next_explicit_copy_cleans_owned_staging"></a>

### `MissingCopyTests.test_restart_records_interruption_and_next_explicit_copy_cleans_owned_staging`

```python
def test_restart_records_interruption_and_next_explicit_copy_cleans_owned_staging(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_running_copy_excludes_another_comparison_and_can_be_stopped"></a>

### `MissingCopyTests.test_running_copy_excludes_another_comparison_and_can_be_stopped`

```python
def test_running_copy_excludes_another_comparison_and_can_be_stopped(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_source_changing_while_reading_leaves_no_final_or_partial_file"></a>

### `MissingCopyTests.test_source_changing_while_reading_leaves_no_final_or_partial_file`

```python
def test_source_changing_while_reading_leaves_no_final_or_partial_file(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_source_replaced_by_fifo_does_not_block_or_copy"></a>

### `MissingCopyTests.test_source_replaced_by_fifo_does_not_block_or_copy`

```python
def test_source_replaced_by_fifo_does_not_block_or_copy(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_stop_removes_only_the_incomplete_staging_file"></a>

### `MissingCopyTests.test_stop_removes_only_the_incomplete_staging_file`

```python
def test_stop_removes_only_the_incomplete_staging_file(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_symlink_target_parent_is_not_followed"></a>

### `MissingCopyTests.test_symlink_target_parent_is_not_followed`

```python
def test_symlink_target_parent_is_not_followed(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_target_appearing_at_publication_is_never_overwritten"></a>

### `MissingCopyTests.test_target_appearing_at_publication_is_never_overwritten`

```python
def test_target_appearing_at_publication_is_never_overwritten(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_target_root_replaced_after_preview_requires_new_preview"></a>

### `MissingCopyTests.test_target_root_replaced_after_preview_requires_new_preview`

```python
def test_target_root_replaced_after_preview_requires_new_preview(self)
```

<a id="symbol-tests.test_copy_files.MissingCopyTests.test_unsupported_atomic_publication_falls_back_without_overwriting"></a>

### `MissingCopyTests.test_unsupported_atomic_publication_falls_back_without_overwriting`

```python
def test_unsupported_atomic_publication_falls_back_without_overwriting(self)
```

<a id="module-tests.test_copy_number_release"></a>

## `test_copy_number_release.py`

Освобождение номеров и история привязок.

[tests/test_copy_number_release.py](../../tests/test_copy_number_release.py)

<a id="symbol-tests.test_copy_number_release.CopyNumberReleaseTests.test_active_main_and_stale_menu_snapshots_cannot_release_a_number"></a>

### `CopyNumberReleaseTests.test_active_main_and_stale_menu_snapshots_cannot_release_a_number`

```python
def test_active_main_and_stale_menu_snapshots_cannot_release_a_number(self)
```

<a id="symbol-tests.test_copy_number_release.CopyNumberReleaseTests.test_api_checks_expected_number_and_active_operations"></a>

### `CopyNumberReleaseTests.test_api_checks_expected_number_and_active_operations`

```python
def test_api_checks_expected_number_and_active_operations(self)
```

<a id="symbol-tests.test_copy_number_release.CopyNumberReleaseTests.test_can_restore_only_when_both_number_and_folder_are_free"></a>

### `CopyNumberReleaseTests.test_can_restore_only_when_both_number_and_folder_are_free`

```python
def test_can_restore_only_when_both_number_and_folder_are_free(self)
```

<a id="symbol-tests.test_copy_number_release.CopyNumberReleaseTests.test_concurrent_additions_reuse_the_released_number_once"></a>

### `CopyNumberReleaseTests.test_concurrent_additions_reuse_the_released_number_once`

```python
def test_concurrent_additions_reuse_the_released_number_once(self)
```

<a id="symbol-tests.test_copy_number_release.CopyNumberReleaseTests.test_old_reports_and_completed_copy_journal_are_not_inherited_by_the_new_copy"></a>

### `CopyNumberReleaseTests.test_old_reports_and_completed_copy_journal_are_not_inherited_by_the_new_copy`

```python
def test_old_reports_and_completed_copy_journal_are_not_inherited_by_the_new_copy(self)
```

<a id="symbol-tests.test_copy_number_release.CopyNumberReleaseTests.test_other_copy_numbers_stay_unchanged_when_a_middle_number_is_released"></a>

### `CopyNumberReleaseTests.test_other_copy_numbers_stay_unchanged_when_a_middle_number_is_released`

```python
def test_other_copy_numbers_stay_unchanged_when_a_middle_number_is_released(self)
```

<a id="symbol-tests.test_copy_number_release.CopyNumberReleaseTests.test_release_is_idempotent_and_group_reconnection_does_not_restore_it"></a>

### `CopyNumberReleaseTests.test_release_is_idempotent_and_group_reconnection_does_not_restore_it`

```python
def test_release_is_idempotent_and_group_reconnection_does_not_restore_it(self)
```

<a id="symbol-tests.test_copy_number_release.CopyNumberReleaseTests.test_released_folder_can_be_rebound_without_inheriting_the_old_identity"></a>

### `CopyNumberReleaseTests.test_released_folder_can_be_rebound_without_inheriting_the_old_identity`

```python
def test_released_folder_can_be_rebound_without_inheriting_the_old_identity(self)
```

<a id="symbol-tests.test_copy_number_release.CopyNumberReleaseTests.test_restoration_rejects_a_folder_now_used_by_another_group"></a>

### `CopyNumberReleaseTests.test_restoration_rejects_a_folder_now_used_by_another_group`

```python
def test_restoration_rejects_a_folder_now_used_by_another_group(self)
```

<a id="symbol-tests.test_copy_number_release.CopyNumberReleaseTests.test_reuses_number_with_a_new_identity_and_preserves_old_record_after_restart"></a>

### `CopyNumberReleaseTests.test_reuses_number_with_a_new_identity_and_preserves_old_record_after_restart`

```python
def test_reuses_number_with_a_new_identity_and_preserves_old_record_after_restart(self)
```

<a id="symbol-tests.test_copy_number_release.CopyNumberReleaseTests.test_upgrade_preserves_existing_disconnections_without_releasing_any_number"></a>

### `CopyNumberReleaseTests.test_upgrade_preserves_existing_disconnections_without_releasing_any_number`

```python
def test_upgrade_preserves_existing_disconnections_without_releasing_any_number(self)
```

<a id="symbol-tests.test_copy_number_release.ReleasedCopyUITests.test_archived_record_stays_in_disconnected_and_opens_history_without_live_folder_reads"></a>

### `ReleasedCopyUITests.test_archived_record_stays_in_disconnected_and_opens_history_without_live_folder_reads`

```python
async def test_archived_record_stays_in_disconnected_and_opens_history_without_live_folder_reads(self)
```

<a id="symbol-tests.test_copy_number_release.ReleasedCopyUITests.test_history_view_does_not_offer_to_create_a_new_binding_from_old_report_paths"></a>

### `ReleasedCopyUITests.test_history_view_does_not_offer_to_create_a_new_binding_from_old_report_paths`

```python
async def test_history_view_does_not_offer_to_create_a_new_binding_from_old_report_paths(self)
```

<a id="symbol-tests.test_copy_number_release.ReleasedCopyUITests.test_history_view_rejects_queued_start_resume_and_copy_commands"></a>

### `ReleasedCopyUITests.test_history_view_rejects_queued_start_resume_and_copy_commands`

```python
async def test_history_view_rejects_queued_start_resume_and_copy_commands(self)
```

<a id="module-tests.test_copy_sandbox"></a>

## `test_copy_sandbox.py`

Запрет записи существующих оригиналов в sandbox.

[tests/test_copy_sandbox.py](../../tests/test_copy_sandbox.py)

<a id="symbol-tests.test_copy_sandbox.CopySandboxTests.test_atomic_copy_keeps_existing_files_write_protected"></a>

### `CopySandboxTests.test_atomic_copy_keeps_existing_files_write_protected`

```python
def test_atomic_copy_keeps_existing_files_write_protected(self)
```

<a id="symbol-tests.test_copy_sandbox.CopySandboxTests.test_folder_marker_write_exception_covers_only_its_service_filename"></a>

### `CopySandboxTests.test_folder_marker_write_exception_covers_only_its_service_filename`

```python
def test_folder_marker_write_exception_covers_only_its_service_filename(self)
```

<a id="symbol-tests.test_copy_sandbox.CopySandboxTests.test_marker_rename_is_atomic_and_keeps_originals_protected"></a>

### `CopySandboxTests.test_marker_rename_is_atomic_and_keeps_originals_protected`

```python
def test_marker_rename_is_atomic_and_keeps_originals_protected(self)
```

<a id="symbol-tests.test_copy_sandbox.CopySandboxTests.test_network_direct_copy_keeps_existing_files_write_protected"></a>

### `CopySandboxTests.test_network_direct_copy_keeps_existing_files_write_protected`

```python
def test_network_direct_copy_keeps_existing_files_write_protected(self)
```

<a id="module-tests.test_copy_sources"></a>

## `test_copy_sources.py`

Выбор источников и запрет циклов обычных копий.

[tests/test_copy_sources.py](../../tests/test_copy_sources.py)

<a id="symbol-tests.test_copy_sources.CopySourceTests.test_change_invalidates_an_old_paused_comparison_and_plan"></a>

### `CopySourceTests.test_change_invalidates_an_old_paused_comparison_and_plan`

```python
def test_change_invalidates_an_old_paused_comparison_and_plan(self)
```

<a id="symbol-tests.test_copy_sources.CopySourceTests.test_cycles_cross_group_sources_and_self_sources_are_rejected"></a>

### `CopySourceTests.test_cycles_cross_group_sources_and_self_sources_are_rejected`

```python
def test_cycles_cross_group_sources_and_self_sources_are_rejected(self)
```

<a id="symbol-tests.test_copy_sources.CopySourceTests.test_disconnected_or_removed_source_never_falls_back_to_original"></a>

### `CopySourceTests.test_disconnected_or_removed_source_never_falls_back_to_original`

```python
def test_disconnected_or_removed_source_never_falls_back_to_original(self)
```

<a id="symbol-tests.test_copy_sources.CopySourceTests.test_old_copy_plan_is_rejected_after_changing_its_source"></a>

### `CopySourceTests.test_old_copy_plan_is_rejected_after_changing_its_source`

```python
def test_old_copy_plan_is_rejected_after_changing_its_source(self)
```

<a id="symbol-tests.test_copy_sources.CopySourceTests.test_second_copy_uses_first_in_comparison_and_actual_transfer"></a>

### `CopySourceTests.test_second_copy_uses_first_in_comparison_and_actual_transfer`

```python
def test_second_copy_uses_first_in_comparison_and_actual_transfer(self)
```

<a id="module-tests.test_directory_sizes"></a>

## `test_directory_sizes.py`

Размеры, частичность, stale и UI-подписи.

[tests/test_directory_sizes.py](../../tests/test_directory_sizes.py)

<a id="symbol-tests.test_directory_sizes.DirectorySizeDisplayTests.test_deleted_rows_are_not_updated_while_a_folder_is_loading"></a>

### `DirectorySizeDisplayTests.test_deleted_rows_are_not_updated_while_a_folder_is_loading`

```python
def test_deleted_rows_are_not_updated_while_a_folder_is_loading(self)
```

<a id="symbol-tests.test_directory_sizes.DirectorySizeDisplayTests.test_header_follows_folder_navigation_and_file_parent_and_hides_missing_side"></a>

### `DirectorySizeDisplayTests.test_header_follows_folder_navigation_and_file_parent_and_hides_missing_side`

```python
def test_header_follows_folder_navigation_and_file_parent_and_hides_missing_side(self)
```

<a id="symbol-tests.test_directory_sizes.DirectorySizeDisplayTests.test_zero_partial_refresh_and_offline_values_are_distinct"></a>

### `DirectorySizeDisplayTests.test_zero_partial_refresh_and_offline_values_are_distinct`

```python
def test_zero_partial_refresh_and_offline_values_are_distinct(self)
```

<a id="symbol-tests.test_directory_sizes.DirectorySizeTests.test_changed_child_invalidates_ancestor_until_it_is_recalculated"></a>

### `DirectorySizeTests.test_changed_child_invalidates_ancestor_until_it_is_recalculated`

```python
def test_changed_child_invalidates_ancestor_until_it_is_recalculated(self)
```

<a id="symbol-tests.test_directory_sizes.DirectorySizeTests.test_failed_refresh_preserves_previous_size"></a>

### `DirectorySizeTests.test_failed_refresh_preserves_previous_size`

```python
def test_failed_refresh_preserves_previous_size(self)
```

<a id="symbol-tests.test_directory_sizes.DirectorySizeTests.test_parent_request_covers_child_without_blocking_or_duplicate_traversals"></a>

### `DirectorySizeTests.test_parent_request_covers_child_without_blocking_or_duplicate_traversals`

```python
def test_parent_request_covers_child_without_blocking_or_duplicate_traversals(self)
```

<a id="symbol-tests.test_directory_sizes.DirectorySizeTests.test_partial_scan_is_not_reported_as_a_complete_folder"></a>

### `DirectorySizeTests.test_partial_scan_is_not_reported_as_a_complete_folder`

```python
def test_partial_scan_is_not_reported_as_a_complete_folder(self)
```

<a id="symbol-tests.test_directory_sizes.DirectorySizeTests.test_paths_links_and_replaced_volumes_are_rejected"></a>

### `DirectorySizeTests.test_paths_links_and_replaced_volumes_are_rejected`

```python
def test_paths_links_and_replaced_volumes_are_rejected(self)
```

<a id="symbol-tests.test_directory_sizes.DirectorySizeTests.test_recursive_totals_include_hidden_files_and_empty_folders_without_opening_contents"></a>

### `DirectorySizeTests.test_recursive_totals_include_hidden_files_and_empty_folders_without_opening_contents`

```python
def test_recursive_totals_include_hidden_files_and_empty_folders_without_opening_contents(self)
```

<a id="symbol-tests.test_directory_sizes.DirectorySizeTests.test_refresh_recomputes_and_cached_result_survives_restart_and_disconnect"></a>

### `DirectorySizeTests.test_refresh_recomputes_and_cached_result_survives_restart_and_disconnect`

```python
def test_refresh_recomputes_and_cached_result_survives_restart_and_disconnect(self)
```

<a id="symbol-tests.test_directory_sizes.DirectorySizeTests.test_reopening_old_cached_size_does_not_scan_again_or_discover_disks"></a>

### `DirectorySizeTests.test_reopening_old_cached_size_does_not_scan_again_or_discover_disks`

```python
def test_reopening_old_cached_size_does_not_scan_again_or_discover_disks(self)
```

<a id="symbol-tests.test_directory_sizes.FolderLoadingTests.test_cached_tree_is_rendered_before_slow_live_directory_read"></a>

### `FolderLoadingTests.test_cached_tree_is_rendered_before_slow_live_directory_read`

```python
async def test_cached_tree_is_rendered_before_slow_live_directory_read(self)
```

<a id="symbol-tests.test_directory_sizes.FolderLoadingTests.test_folder_list_does_not_wait_for_a_blocked_size_request"></a>

### `FolderLoadingTests.test_folder_list_does_not_wait_for_a_blocked_size_request`

```python
async def test_folder_list_does_not_wait_for_a_blocked_size_request(self)
```

<a id="symbol-tests.test_directory_sizes.RefreshButtonTests.test_completed_failed_and_offline_calculations_release_the_button"></a>

### `RefreshButtonTests.test_completed_failed_and_offline_calculations_release_the_button`

```python
async def test_completed_failed_and_offline_calculations_release_the_button(self)
```

<a id="symbol-tests.test_directory_sizes.RefreshButtonTests.test_failed_size_request_releases_the_button_without_queuing_another_request"></a>

### `RefreshButtonTests.test_failed_size_request_releases_the_button_without_queuing_another_request`

```python
async def test_failed_size_request_releases_the_button_without_queuing_another_request(self)
```

<a id="symbol-tests.test_directory_sizes.RefreshButtonTests.test_forced_refresh_does_not_recalculate_other_visible_folders"></a>

### `RefreshButtonTests.test_forced_refresh_does_not_recalculate_other_visible_folders`

```python
async def test_forced_refresh_does_not_recalculate_other_visible_folders(self)
```

<a id="symbol-tests.test_directory_sizes.RefreshButtonTests.test_navigation_during_refresh_does_not_clear_the_new_folder"></a>

### `RefreshButtonTests.test_navigation_during_refresh_does_not_clear_the_new_folder`

```python
async def test_navigation_during_refresh_does_not_clear_the_new_folder(self)
```

<a id="symbol-tests.test_directory_sizes.RefreshButtonTests.test_rapid_clicks_and_second_pane_do_not_repeat_refresh_until_calculation_finishes"></a>

### `RefreshButtonTests.test_rapid_clicks_and_second_pane_do_not_repeat_refresh_until_calculation_finishes`

```python
async def test_rapid_clicks_and_second_pane_do_not_repeat_refresh_until_calculation_finishes(self)
```

<a id="module-tests.test_documentation"></a>

## `test_documentation.py`

Устойчивость генерации, одноимённые определения, актуальность, комментарии и ссылки.

[tests/test_documentation.py](../../tests/test_documentation.py)

<a id="symbol-tests.test_documentation.DocumentationTests.test_changed_marked_explanation_updates_corresponding_description"></a>

### `DocumentationTests.test_changed_marked_explanation_updates_corresponding_description`

```python
def test_changed_marked_explanation_updates_corresponding_description(self)
```

<a id="symbol-tests.test_documentation.DocumentationTests.test_contract_change_updates_only_its_definition"></a>

### `DocumentationTests.test_contract_change_updates_only_its_definition`

```python
def test_contract_change_updates_only_its_definition(self)
```

<a id="symbol-tests.test_documentation.DocumentationTests.test_duplicate_names_preserve_scope_case_and_declaration_identity"></a>

### `DocumentationTests.test_duplicate_names_preserve_scope_case_and_declaration_identity`

```python
def test_duplicate_names_preserve_scope_case_and_declaration_identity(self)
```

<a id="symbol-tests.test_documentation.DocumentationTests.test_line_shifts_and_ordinary_comments_produce_no_document_changes"></a>

### `DocumentationTests.test_line_shifts_and_ordinary_comments_produce_no_document_changes`

```python
def test_line_shifts_and_ordinary_comments_produce_no_document_changes(self)
```

<a id="symbol-tests.test_documentation.DocumentationTests.test_link_to_removed_definition_is_detected"></a>

### `DocumentationTests.test_link_to_removed_definition_is_detected`

```python
def test_link_to_removed_definition_is_detected(self)
```

<a id="symbol-tests.test_documentation.DocumentationTests.test_missing_explanation_is_detected_even_with_ordinary_comments"></a>

### `DocumentationTests.test_missing_explanation_is_detected_even_with_ordinary_comments`

```python
def test_missing_explanation_is_detected_even_with_ordinary_comments(self)
```

<a id="symbol-tests.test_documentation.DocumentationTests.test_missing_file_and_physical_line_link_are_detected"></a>

### `DocumentationTests.test_missing_file_and_physical_line_link_are_detected`

```python
def test_missing_file_and_physical_line_link_are_detected(self)
```

<a id="symbol-tests.test_documentation.DocumentationTests.test_missing_module_and_unregistered_module_are_detected"></a>

### `DocumentationTests.test_missing_module_and_unregistered_module_are_detected`

```python
def test_missing_module_and_unregistered_module_are_detected(self)
```

<a id="symbol-tests.test_documentation.DocumentationTests.test_native_definition_ignores_line_shifts_and_ordinary_comments"></a>

### `DocumentationTests.test_native_definition_ignores_line_shifts_and_ordinary_comments`

```python
def test_native_definition_ignores_line_shifts_and_ordinary_comments(self)
```

<a id="symbol-tests.test_documentation.DocumentationTests.test_orphaned_reference_page_is_detected"></a>

### `DocumentationTests.test_orphaned_reference_page_is_detected`

```python
def test_orphaned_reference_page_is_detected(self)
```

<a id="symbol-tests.test_documentation.DocumentationTests.test_release_hash_is_preserved_as_semantic_constant"></a>

### `DocumentationTests.test_release_hash_is_preserved_as_semantic_constant`

```python
def test_release_hash_is_preserved_as_semantic_constant(self)
```

<a id="symbol-tests.test_documentation.DocumentationTests.test_removed_function_is_reported_as_stale"></a>

### `DocumentationTests.test_removed_function_is_reported_as_stale`

```python
def test_removed_function_is_reported_as_stale(self)
```

<a id="symbol-tests.test_documentation.DocumentationTests.test_vue_watch_and_method_with_same_name_have_distinct_anchors"></a>

### `DocumentationTests.test_vue_watch_and_method_with_same_name_have_distinct_anchors`

```python
def test_vue_watch_and_method_with_same_name_have_distinct_anchors(self)
```

<a id="module-tests.test_folder_markers"></a>

## `test_folder_markers.py`

Принадлежность, публикация и повтор маркеров папок.

[tests/test_folder_markers.py](../../tests/test_folder_markers.py)

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_a_marker_appearing_during_creation_is_not_overwritten"></a>

### `FolderMarkerTests.test_a_marker_appearing_during_creation_is_not_overwritten`

```python
def test_a_marker_appearing_during_creation_is_not_overwritten(self)
```

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_all_registered_roots_get_own_ids_and_readable_roles_without_changing_data"></a>

### `FolderMarkerTests.test_all_registered_roots_get_own_ids_and_readable_roles_without_changing_data`

```python
def test_all_registered_roots_get_own_ids_and_readable_roles_without_changing_data(self)
```

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_connection_kind_and_release_changes_reach_the_same_folder_marker"></a>

### `FolderMarkerTests.test_connection_kind_and_release_changes_reach_the_same_folder_marker`

```python
def test_connection_kind_and_release_changes_reach_the_same_folder_marker(self)
```

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_deleted_bindings_are_marked_removed_without_deleting_source_files"></a>

### `FolderMarkerTests.test_deleted_bindings_are_marked_removed_without_deleting_source_files`

```python
def test_deleted_bindings_are_marked_removed_without_deleting_source_files(self)
```

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_existing_catalog_backfill_and_pending_changes_survive_restart"></a>

### `FolderMarkerTests.test_existing_catalog_backfill_and_pending_changes_survive_restart`

```python
def test_existing_catalog_backfill_and_pending_changes_survive_restart(self)
```

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_failed_atomic_update_preserves_the_previous_document_and_cleans_temporary_files"></a>

### `FolderMarkerTests.test_failed_atomic_update_preserves_the_previous_document_and_cleans_temporary_files`

```python
def test_failed_atomic_update_preserves_the_previous_document_and_cleans_temporary_files(self)
```

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_foreign_marker_symlink_fifo_and_oversized_file_are_preserved"></a>

### `FolderMarkerTests.test_foreign_marker_symlink_fifo_and_oversized_file_are_preserved`

```python
def test_foreign_marker_symlink_fifo_and_oversized_file_are_preserved(self)
```

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_metadata_change_during_a_write_keeps_the_newer_revision_pending"></a>

### `FolderMarkerTests.test_metadata_change_during_a_write_keeps_the_newer_revision_pending`

```python
def test_metadata_change_during_a_write_keeps_the_newer_revision_pending(self)
```

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_offline_or_missing_folder_is_retried_without_creating_directories"></a>

### `FolderMarkerTests.test_offline_or_missing_folder_is_retried_without_creating_directories`

```python
def test_offline_or_missing_folder_is_retried_without_creating_directories(self)
```

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_only_the_latest_binding_can_describe_a_path_with_several_old_generations"></a>

### `FolderMarkerTests.test_only_the_latest_binding_can_describe_a_path_with_several_old_generations`

```python
def test_only_the_latest_binding_can_describe_a_path_with_several_old_generations(self)
```

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_rechecking_unchanged_markers_does_not_rewrite_the_files"></a>

### `FolderMarkerTests.test_rechecking_unchanged_markers_does_not_rewrite_the_files`

```python
def test_rechecking_unchanged_markers_does_not_rewrite_the_files(self)
```

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_reusing_a_released_path_writes_the_new_identity_without_old_job_overwriting_it"></a>

### `FolderMarkerTests.test_reusing_a_released_path_writes_the_new_identity_without_old_job_overwriting_it`

```python
def test_reusing_a_released_path_writes_the_new_identity_without_old_job_overwriting_it(self)
```

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_service_files_are_excluded_from_lists_sizes_both_comparisons_and_data_copying"></a>

### `FolderMarkerTests.test_service_files_are_excluded_from_lists_sizes_both_comparisons_and_data_copying`

```python
def test_service_files_are_excluded_from_lists_sizes_both_comparisons_and_data_copying(self)
```

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_smb_exclusive_creation_fallback_still_never_overwrites_existing_files"></a>

### `FolderMarkerTests.test_smb_exclusive_creation_fallback_still_never_overwrites_existing_files`

```python
def test_smb_exclusive_creation_fallback_still_never_overwrites_existing_files(self)
```

<a id="symbol-tests.test_folder_markers.FolderMarkerTests.test_unverified_volume_never_receives_folder_writes"></a>

### `FolderMarkerTests.test_unverified_volume_never_receives_folder_writes`

```python
def test_unverified_volume_never_receives_folder_writes(self)
```

<a id="module-tests.test_folder_tags"></a>

## `test_folder_tags.py`

Пользовательские метки папок.

[tests/test_folder_tags.py](../../tests/test_folder_tags.py)

<a id="symbol-tests.test_folder_tags.FolderTagTests.test_api_supports_multiple_tags_and_forbids_the_automatic_library_tag"></a>

### `FolderTagTests.test_api_supports_multiple_tags_and_forbids_the_automatic_library_tag`

```python
def test_api_supports_multiple_tags_and_forbids_the_automatic_library_tag(self)
```

<a id="symbol-tests.test_folder_tags.FolderTagTests.test_files_symlinks_unknown_paths_and_traversal_cannot_receive_folder_tags"></a>

### `FolderTagTests.test_files_symlinks_unknown_paths_and_traversal_cannot_receive_folder_tags`

```python
def test_files_symlinks_unknown_paths_and_traversal_cannot_receive_folder_tags(self)
```

<a id="symbol-tests.test_folder_tags.FolderTagTests.test_multiple_tags_persist_without_changing_annotations_or_original_files"></a>

### `FolderTagTests.test_multiple_tags_persist_without_changing_annotations_or_original_files`

```python
def test_multiple_tags_persist_without_changing_annotations_or_original_files(self)
```

<a id="symbol-tests.test_folder_tags.FolderTagTests.test_old_database_gains_tag_table_without_losing_existing_metadata"></a>

### `FolderTagTests.test_old_database_gains_tag_table_without_losing_existing_metadata`

```python
def test_old_database_gains_tag_table_without_losing_existing_metadata(self)
```

<a id="symbol-tests.test_folder_tags.FolderTagTests.test_saved_tag_changes_update_both_open_trees_without_reloading_directories"></a>

### `FolderTagTests.test_saved_tag_changes_update_both_open_trees_without_reloading_directories`

```python
def test_saved_tag_changes_update_both_open_trees_without_reloading_directories(self)
```

<a id="symbol-tests.test_folder_tags.FolderTagTests.test_system_and_unknown_tags_are_rejected_without_changing_existing_tags"></a>

### `FolderTagTests.test_system_and_unknown_tags_are_rejected_without_changing_existing_tags`

```python
def test_system_and_unknown_tags_are_rejected_without_changing_existing_tags(self)
```

<a id="symbol-tests.test_folder_tags.FolderTagTests.test_tags_apply_only_to_the_selected_folder_and_update_cached_listings"></a>

### `FolderTagTests.test_tags_apply_only_to_the_selected_folder_and_update_cached_listings`

```python
def test_tags_apply_only_to_the_selected_folder_and_update_cached_listings(self)
```

<a id="symbol-tests.test_folder_tags.FolderTagTests.test_tags_do_not_transfer_to_another_disk_at_the_same_mount_point"></a>

### `FolderTagTests.test_tags_do_not_transfer_to_another_disk_at_the_same_mount_point`

```python
def test_tags_do_not_transfer_to_another_disk_at_the_same_mount_point(self)
```

<a id="module-tests.test_folder_tracking"></a>

## `test_folder_tracking.py`

Watchdog и подтверждение изменений.

[tests/test_folder_tracking.py](../../tests/test_folder_tracking.py)

<a id="symbol-tests.test_folder_tracking.FolderTrackingTests.test_actual_observer_detects_nested_file_changes"></a>

### `FolderTrackingTests.test_actual_observer_detects_nested_file_changes`

```python
def test_actual_observer_detects_nested_file_changes(self)
```

<a id="symbol-tests.test_folder_tracking.FolderTrackingTests.test_api_settings_validation_and_partial_updates"></a>

### `FolderTrackingTests.test_api_settings_validation_and_partial_updates`

```python
def test_api_settings_validation_and_partial_updates(self)
```

<a id="symbol-tests.test_folder_tracking.FolderTrackingTests.test_manual_group_disconnect_stops_tracking_until_reconnected"></a>

### `FolderTrackingTests.test_manual_group_disconnect_stops_tracking_until_reconnected`

```python
def test_manual_group_disconnect_stops_tracking_until_reconnected(self)
```

<a id="symbol-tests.test_folder_tracking.FolderTrackingTests.test_offline_and_disabled_folders_detach_and_stale_events_are_ignored"></a>

### `FolderTrackingTests.test_offline_and_disabled_folders_detach_and_stale_events_are_ignored`

```python
def test_offline_and_disabled_folders_detach_and_stale_events_are_ignored(self)
```

<a id="symbol-tests.test_folder_tracking.FolderTrackingTests.test_only_opted_in_folders_subscribe_and_events_persist_after_restart"></a>

### `FolderTrackingTests.test_only_opted_in_folders_subscribe_and_events_persist_after_restart`

```python
def test_only_opted_in_folders_subscribe_and_events_persist_after_restart(self)
```

<a id="symbol-tests.test_folder_tracking.FolderTrackingTests.test_read_events_and_copy_temporaries_do_not_trigger_a_change"></a>

### `FolderTrackingTests.test_read_events_and_copy_temporaries_do_not_trigger_a_change`

```python
def test_read_events_and_copy_temporaries_do_not_trigger_a_change(self)
```

<a id="symbol-tests.test_folder_tracking.FolderTrackingTests.test_reconnect_restores_tracking_and_replaced_or_symlink_roots_are_rejected"></a>

### `FolderTrackingTests.test_reconnect_restores_tracking_and_replaced_or_symlink_roots_are_rejected`

```python
def test_reconnect_restores_tracking_and_replaced_or_symlink_roots_are_rejected(self)
```

<a id="module-tests.test_network"></a>

## `test_network.py`

Bonjour, ресурсы SMB и ошибки.

[tests/test_network.py](../../tests/test_network.py)

<a id="symbol-tests.test_network.NetworkCatalogTests.test_auth_error_preserves_share_list"></a>

### `NetworkCatalogTests.test_auth_error_preserves_share_list`

```python
def test_auth_error_preserves_share_list(self)
```

<a id="symbol-tests.test_network.NetworkCatalogTests.test_existing_volume_keeps_identity_role_and_snapshot"></a>

### `NetworkCatalogTests.test_existing_volume_keeps_identity_role_and_snapshot`

```python
def test_existing_volume_keeps_identity_role_and_snapshot(self)
```

<a id="symbol-tests.test_network.NetworkCatalogTests.test_failed_scan_preserves_previous_discovery"></a>

### `NetworkCatalogTests.test_failed_scan_preserves_previous_discovery`

```python
def test_failed_scan_preserves_previous_discovery(self)
```

<a id="symbol-tests.test_network.NetworkCatalogTests.test_legacy_offline_group_is_matched_by_identity_not_share_name"></a>

### `NetworkCatalogTests.test_legacy_offline_group_is_matched_by_identity_not_share_name`

```python
def test_legacy_offline_group_is_matched_by_identity_not_share_name(self)
```

<a id="symbol-tests.test_network.NetworkCatalogTests.test_legacy_volume_table_is_not_altered"></a>

### `NetworkCatalogTests.test_legacy_volume_table_is_not_altered`

```python
def test_legacy_volume_table_is_not_altered(self)
```

<a id="symbol-tests.test_network.NetworkCatalogTests.test_nas_and_m4_groups_survive_disconnection_and_restart"></a>

### `NetworkCatalogTests.test_nas_and_m4_groups_survive_disconnection_and_restart`

```python
def test_nas_and_m4_groups_survive_disconnection_and_restart(self)
```

<a id="symbol-tests.test_network.NetworkCatalogTests.test_offline_server_and_missing_resource_remain_remembered"></a>

### `NetworkCatalogTests.test_offline_server_and_missing_resource_remain_remembered`

```python
def test_offline_server_and_missing_resource_remain_remembered(self)
```

<a id="symbol-tests.test_network.NetworkCatalogTests.test_remember_unmounted_resource_and_roles_without_os_actions"></a>

### `NetworkCatalogTests.test_remember_unmounted_resource_and_roles_without_os_actions`

```python
def test_remember_unmounted_resource_and_roles_without_os_actions(self)
```

<a id="symbol-tests.test_network.NetworkCatalogTests.test_resource_matches_mount_by_other_bonjour_alias_without_duplicate"></a>

### `NetworkCatalogTests.test_resource_matches_mount_by_other_bonjour_alias_without_duplicate`

```python
def test_resource_matches_mount_by_other_bonjour_alias_without_duplicate(self)
```

<a id="symbol-tests.test_network.NetworkCatalogTests.test_same_share_names_on_different_servers_stay_in_separate_groups"></a>

### `NetworkCatalogTests.test_same_share_names_on_different_servers_stay_in_separate_groups`

```python
def test_same_share_names_on_different_servers_stay_in_separate_groups(self)
```

<a id="symbol-tests.test_network.NetworkCatalogTests.test_unknown_share_is_rejected_and_finder_requires_explicit_command"></a>

### `NetworkCatalogTests.test_unknown_share_is_rejected_and_finder_requires_explicit_command`

```python
def test_unknown_share_is_rejected_and_finder_requires_explicit_command(self)
```

<a id="symbol-tests.test_network.NetworkParsingTests.test_bonjour_keeps_other_interface_after_remove"></a>

### `NetworkParsingTests.test_bonjour_keeps_other_interface_after_remove`

```python
def test_bonjour_keeps_other_interface_after_remove(self)
```

<a id="symbol-tests.test_network.NetworkParsingTests.test_diagnostics_do_not_expose_account_or_password"></a>

### `NetworkParsingTests.test_diagnostics_do_not_expose_account_or_password`

```python
def test_diagnostics_do_not_expose_account_or_password(self)
```

<a id="symbol-tests.test_network.NetworkParsingTests.test_discovery_merges_two_advertisements_of_same_server"></a>

### `NetworkParsingTests.test_discovery_merges_two_advertisements_of_same_server`

```python
def test_discovery_merges_two_advertisements_of_same_server(self)
```

<a id="symbol-tests.test_network.NetworkParsingTests.test_lists_disk_shares_only_and_keeps_spaces_unicode"></a>

### `NetworkParsingTests.test_lists_disk_shares_only_and_keeps_spaces_unicode`

```python
def test_lists_disk_shares_only_and_keeps_spaces_unicode(self)
```

<a id="symbol-tests.test_network.NetworkParsingTests.test_no_password_prompt_or_mount_in_share_enumeration"></a>

### `NetworkParsingTests.test_no_password_prompt_or_mount_in_share_enumeration`

```python
def test_no_password_prompt_or_mount_in_share_enumeration(self)
```

<a id="module-tests.test_paired_comparison"></a>

## `test_paired_comparison.py`

Выровненная структура, размеры и SHA-256.

[tests/test_paired_comparison.py](../../tests/test_paired_comparison.py)

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_default_file_check_compares_names_and_sizes_without_reading_contents"></a>

### `PairedComparisonTests.test_default_file_check_compares_names_and_sizes_without_reading_contents`

```python
def test_default_file_check_compares_names_and_sizes_without_reading_contents(self)
```

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_difference_pages_keep_root_folders_alongside_differences_and_their_parents"></a>

### `PairedComparisonTests.test_difference_pages_keep_root_folders_alongside_differences_and_their_parents`

```python
def test_difference_pages_keep_root_folders_alongside_differences_and_their_parents(self)
```

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_extra_copy_decisions_are_records_and_do_not_change_disks"></a>

### `PairedComparisonTests.test_extra_copy_decisions_are_records_and_do_not_change_disks`

```python
def test_extra_copy_decisions_are_records_and_do_not_change_disks(self)
```

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_failed_directory_does_not_turn_unknown_data_into_absence"></a>

### `PairedComparisonTests.test_failed_directory_does_not_turn_unknown_data_into_absence`

```python
def test_failed_directory_does_not_turn_unknown_data_into_absence(self)
```

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_file_changed_while_hashing_is_unverified"></a>

### `PairedComparisonTests.test_file_changed_while_hashing_is_unverified`

```python
def test_file_changed_while_hashing_is_unverified(self)
```

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_folder_comparison_uses_relative_paths_and_reports_both_directions"></a>

### `PairedComparisonTests.test_folder_comparison_uses_relative_paths_and_reports_both_directions`

```python
def test_folder_comparison_uses_relative_paths_and_reports_both_directions(self)
```

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_folder_decisions_inherit_and_survive_the_file_stage"></a>

### `PairedComparisonTests.test_folder_decisions_inherit_and_survive_the_file_stage`

```python
def test_folder_decisions_inherit_and_survive_the_file_stage(self)
```

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_folder_stage_never_opens_file_contents"></a>

### `PairedComparisonTests.test_folder_stage_never_opens_file_contents`

```python
def test_folder_stage_never_opens_file_contents(self)
```

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_full_stage_checks_content_and_keeps_files_original"></a>

### `PairedComparisonTests.test_full_stage_checks_content_and_keeps_files_original`

```python
def test_full_stage_checks_content_and_keeps_files_original(self)
```

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_full_stage_requires_finished_folder_check_for_same_pair"></a>

### `PairedComparisonTests.test_full_stage_requires_finished_folder_check_for_same_pair`

```python
def test_full_stage_requires_finished_folder_check_for_same_pair(self)
```

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_matching_reports_keep_root_folders_without_matching_files_for_both_methods"></a>

### `PairedComparisonTests.test_matching_reports_keep_root_folders_without_matching_files_for_both_methods`

```python
def test_matching_reports_keep_root_folders_without_matching_files_for_both_methods(self)
```

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_offline_side_is_unknown_and_interrupted_jobs_can_be_resumed"></a>

### `PairedComparisonTests.test_offline_side_is_unknown_and_interrupted_jobs_can_be_resumed`

```python
def test_offline_side_is_unknown_and_interrupted_jobs_can_be_resumed(self)
```

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_pause_resume_restart_and_saved_results"></a>

### `PairedComparisonTests.test_pause_resume_restart_and_saved_results`

```python
def test_pause_resume_restart_and_saved_results(self)
```

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_symlinks_and_special_files_are_not_followed_and_type_conflicts_are_visible"></a>

### `PairedComparisonTests.test_symlinks_and_special_files_are_not_followed_and_type_conflicts_are_visible`

```python
def test_symlinks_and_special_files_are_not_followed_and_type_conflicts_are_visible(self)
```

<a id="symbol-tests.test_paired_comparison.PairedComparisonTests.test_upgrade_preserves_old_reports_as_sha256"></a>

### `PairedComparisonTests.test_upgrade_preserves_old_reports_as_sha256`

```python
def test_upgrade_preserves_old_reports_as_sha256(self)
```

<a id="module-tests.test_paired_workspace"></a>

## `test_paired_workspace.py`

Связанные панели, просмотр и история.

[tests/test_paired_workspace.py](../../tests/test_paired_workspace.py)

<a id="symbol-tests.test_paired_workspace.BreadcrumbNavigationTests.test_delayed_selector_event_cannot_reset_the_clicked_parent"></a>

### `BreadcrumbNavigationTests.test_delayed_selector_event_cannot_reset_the_clicked_parent`

```python
async def test_delayed_selector_event_cannot_reset_the_clicked_parent(self)
```

<a id="symbol-tests.test_paired_workspace.BreadcrumbNavigationTests.test_opening_parent_uses_existing_unlink_without_removing_records"></a>

### `BreadcrumbNavigationTests.test_opening_parent_uses_existing_unlink_without_removing_records`

```python
async def test_opening_parent_uses_existing_unlink_without_removing_records(self)
```

<a id="symbol-tests.test_paired_workspace.BreadcrumbNavigationTests.test_parent_and_volume_root_leave_the_pair_on_the_clicked_side"></a>

### `BreadcrumbNavigationTests.test_parent_and_volume_root_leave_the_pair_on_the_clicked_side`

```python
async def test_parent_and_volume_root_leave_the_pair_on_the_clicked_side(self)
```

<a id="symbol-tests.test_paired_workspace.BreadcrumbNavigationTests.test_source_report_parent_opens_normal_browsing"></a>

### `BreadcrumbNavigationTests.test_source_report_parent_opens_normal_browsing`

```python
async def test_source_report_parent_opens_normal_browsing(self)
```

<a id="symbol-tests.test_paired_workspace.ComparisonToolbarTests.test_all_three_actions_ignore_queued_clicks_in_any_comparison_state"></a>

### `ComparisonToolbarTests.test_all_three_actions_ignore_queued_clicks_in_any_comparison_state`

```python
async def test_all_three_actions_ignore_queued_clicks_in_any_comparison_state(self)
```

<a id="symbol-tests.test_paired_workspace.ComparisonToolbarTests.test_linked_browsing_without_a_report_keeps_navigation_available"></a>

### `ComparisonToolbarTests.test_linked_browsing_without_a_report_keeps_navigation_available`

```python
async def test_linked_browsing_without_a_report_keeps_navigation_available(self)
```

<a id="symbol-tests.test_paired_workspace.CopyRemovalConfirmationTests.test_cancel_shows_both_locations_without_deleting_the_link"></a>

### `CopyRemovalConfirmationTests.test_cancel_shows_both_locations_without_deleting_the_link`

```python
async def test_cancel_shows_both_locations_without_deleting_the_link(self)
```

<a id="symbol-tests.test_paired_workspace.CopyRemovalConfirmationTests.test_confirm_removes_only_the_chosen_link_then_closes_its_pair"></a>

### `CopyRemovalConfirmationTests.test_confirm_removes_only_the_chosen_link_then_closes_its_pair`

```python
async def test_confirm_removes_only_the_chosen_link_then_closes_its_pair(self)
```

<a id="symbol-tests.test_paired_workspace.MainFolderOpeningTests.test_main_opens_the_first_numbered_copy_in_linked_panels"></a>

### `MainFolderOpeningTests.test_main_opens_the_first_numbered_copy_in_linked_panels`

```python
async def test_main_opens_the_first_numbered_copy_in_linked_panels(self)
```

<a id="symbol-tests.test_paired_workspace.MainFolderOpeningTests.test_main_without_copies_opens_only_the_main_folder"></a>

### `MainFolderOpeningTests.test_main_without_copies_opens_only_the_main_folder`

```python
async def test_main_without_copies_opens_only_the_main_folder(self)
```

<a id="symbol-tests.test_paired_workspace.PairedContextMenuTests.test_finder_uses_the_clicked_side_and_its_full_volume_path"></a>

### `PairedContextMenuTests.test_finder_uses_the_clicked_side_and_its_full_volume_path`

```python
async def test_finder_uses_the_clicked_side_and_its_full_volume_path(self)
```

<a id="symbol-tests.test_paired_workspace.PairedContextMenuTests.test_missing_side_does_not_open_another_sides_file"></a>

### `PairedContextMenuTests.test_missing_side_does_not_open_another_sides_file`

```python
async def test_missing_side_does_not_open_another_sides_file(self)
```

<a id="symbol-tests.test_paired_workspace.PairedContextMenuTests.test_open_menu_blocks_background_refresh_until_closed"></a>

### `PairedContextMenuTests.test_open_menu_blocks_background_refresh_until_closed`

```python
async def test_open_menu_blocks_background_refresh_until_closed(self)
```

<a id="symbol-tests.test_paired_workspace.PairedContextMenuTests.test_properties_and_decisions_remain_separate_menu_actions"></a>

### `PairedContextMenuTests.test_properties_and_decisions_remain_separate_menu_actions`

```python
async def test_properties_and_decisions_remain_separate_menu_actions(self)
```

<a id="symbol-tests.test_paired_workspace.PairedWorkspaceTests.test_expanding_one_folder_reveals_only_its_differing_files"></a>

### `PairedWorkspaceTests.test_expanding_one_folder_reveals_only_its_differing_files`

```python
def test_expanding_one_folder_reveals_only_its_differing_files(self)
```

<a id="symbol-tests.test_paired_workspace.PairedWorkspaceTests.test_fully_matching_report_keeps_root_folders_collapsed"></a>

### `PairedWorkspaceTests.test_fully_matching_report_keeps_root_folders_collapsed`

```python
def test_fully_matching_report_keeps_root_folders_collapsed(self)
```

<a id="symbol-tests.test_paired_workspace.PairedWorkspaceTests.test_root_files_require_explicit_disclosure_even_after_navigation"></a>

### `PairedWorkspaceTests.test_root_files_require_explicit_disclosure_even_after_navigation`

```python
def test_root_files_require_explicit_disclosure_even_after_navigation(self)
```

<a id="symbol-tests.test_paired_workspace.PanelUnlinkTests.test_leaving_a_running_comparison_stops_it_before_restoring_the_panels"></a>

### `PanelUnlinkTests.test_leaving_a_running_comparison_stops_it_before_restoring_the_panels`

```python
async def test_leaving_a_running_comparison_stops_it_before_restoring_the_panels(self)
```

<a id="symbol-tests.test_paired_workspace.PanelUnlinkTests.test_panel_unlink_restores_browsing_without_removing_copy_records"></a>

### `PanelUnlinkTests.test_panel_unlink_restores_browsing_without_removing_copy_records`

```python
async def test_panel_unlink_restores_browsing_without_removing_copy_records(self)
```

<a id="symbol-tests.test_paired_workspace.ReportExpansionTests.test_file_stage_still_leaves_every_folder_closed_until_manual_expansion"></a>

### `ReportExpansionTests.test_file_stage_still_leaves_every_folder_closed_until_manual_expansion`

```python
async def test_file_stage_still_leaves_every_folder_closed_until_manual_expansion(self)
```

<a id="symbol-tests.test_paired_workspace.ReportExpansionTests.test_only_branches_with_differences_expand_and_manual_changes_survive_reload"></a>

### `ReportExpansionTests.test_only_branches_with_differences_expand_and_manual_changes_survive_reload`

```python
async def test_only_branches_with_differences_expand_and_manual_changes_survive_reload(self)
```

<a id="module-tests.test_photo_copy_roles"></a>

## `test_photo_copy_roles.py`

Метки привязанных копий Photos.

[tests/test_photo_copy_roles.py](../../tests/test_photo_copy_roles.py)

<a id="symbol-tests.test_photo_copy_roles.PhotoCopyRoleTests.test_bound_copy_has_its_own_number_and_library_tag_while_photos_is_offline"></a>

### `PhotoCopyRoleTests.test_bound_copy_has_its_own_number_and_library_tag_while_photos_is_offline`

```python
def test_bound_copy_has_its_own_number_and_library_tag_while_photos_is_offline(self)
```

<a id="symbol-tests.test_photo_copy_roles.PhotoCopyRoleTests.test_disconnecting_library_copy_removes_its_tags_and_preserves_other_roles"></a>

### `PhotoCopyRoleTests.test_disconnecting_library_copy_removes_its_tags_and_preserves_other_roles`

```python
def test_disconnecting_library_copy_removes_its_tags_and_preserves_other_roles(self)
```

<a id="symbol-tests.test_photo_copy_roles.PhotoCopyRoleTests.test_only_the_exact_bound_folder_gets_the_library_role"></a>

### `PhotoCopyRoleTests.test_only_the_exact_bound_folder_gets_the_library_role`

```python
def test_only_the_exact_bound_folder_gets_the_library_role(self)
```

<a id="symbol-tests.test_photo_copy_roles.PhotoCopyRoleTests.test_refresh_updates_tags_after_rebinding_but_not_on_progress_changes"></a>

### `PhotoCopyRoleTests.test_refresh_updates_tags_after_rebinding_but_not_on_progress_changes`

```python
def test_refresh_updates_tags_after_rebinding_but_not_on_progress_changes(self)
```

<a id="module-tests.test_photo_libraries"></a>

## `test_photo_libraries.py`

Идентичность и профили медиатек.

[tests/test_photo_libraries.py](../../tests/test_photo_libraries.py)

<a id="symbol-tests.test_photo_libraries.PhotoLibrariesTests.test_cloud_waits_do_not_block_the_next_asset_or_count_as_errors"></a>

### `PhotoLibrariesTests.test_cloud_waits_do_not_block_the_next_asset_or_count_as_errors`

```python
def test_cloud_waits_do_not_block_the_next_asset_or_count_as_errors(self)
```

<a id="symbol-tests.test_photo_libraries.PhotoLibrariesTests.test_copy_binding_and_unbinding_never_write_originals_or_touch_destination_files"></a>

### `PhotoLibrariesTests.test_copy_binding_and_unbinding_never_write_originals_or_touch_destination_files`

```python
def test_copy_binding_and_unbinding_never_write_originals_or_touch_destination_files(self)
```

<a id="symbol-tests.test_photo_libraries.PhotoLibrariesTests.test_copy_receipts_are_metadata_only_and_survive_removed_photos"></a>

### `PhotoLibrariesTests.test_copy_receipts_are_metadata_only_and_survive_removed_photos`

```python
def test_copy_receipts_are_metadata_only_and_survive_removed_photos(self)
```

<a id="symbol-tests.test_photo_libraries.PhotoLibrariesTests.test_copy_targets_reject_symlinks_parent_traversal_and_overlapping_libraries"></a>

### `PhotoLibrariesTests.test_copy_targets_reject_symlinks_parent_traversal_and_overlapping_libraries`

```python
def test_copy_targets_reject_symlinks_parent_traversal_and_overlapping_libraries(self)
```

<a id="symbol-tests.test_photo_libraries.PhotoLibrariesTests.test_migration_preserves_media_ids_and_existing_cached_previews_without_access"></a>

### `PhotoLibrariesTests.test_migration_preserves_media_ids_and_existing_cached_previews_without_access`

```python
def test_migration_preserves_media_ids_and_existing_cached_previews_without_access(self)
```

<a id="symbol-tests.test_photo_libraries.PhotoLibrariesTests.test_photokit_scan_without_resource_sizes_preserves_known_original_sizes"></a>

### `PhotoLibrariesTests.test_photokit_scan_without_resource_sizes_preserves_known_original_sizes`

```python
def test_photokit_scan_without_resource_sizes_preserves_known_original_sizes(self)
```

<a id="symbol-tests.test_photo_libraries.PhotoLibrariesTests.test_renaming_survives_legacy_source_registration_and_restart"></a>

### `PhotoLibrariesTests.test_renaming_survives_legacy_source_registration_and_restart`

```python
def test_renaming_survives_legacy_source_registration_and_restart(self)
```

<a id="symbol-tests.test_photo_libraries.PhotoLibrariesTests.test_resuming_photos_does_not_resume_the_paused_folder_queue_and_includes_video"></a>

### `PhotoLibrariesTests.test_resuming_photos_does_not_resume_the_paused_folder_queue_and_includes_video`

```python
def test_resuming_photos_does_not_resume_the_paused_folder_queue_and_includes_video(self)
```

<a id="symbol-tests.test_photo_libraries.PhotoLibrariesTests.test_sidebar_progress_and_cloud_wait_states_are_separate"></a>

### `PhotoLibrariesTests.test_sidebar_progress_and_cloud_wait_states_are_separate`

```python
def test_sidebar_progress_and_cloud_wait_states_are_separate(self)
```

<a id="symbol-tests.test_photo_libraries.PhotoLibrariesTests.test_small_photokit_preview_stays_visible_while_waiting_for_a_larger_local_image"></a>

### `PhotoLibrariesTests.test_small_photokit_preview_stays_visible_while_waiting_for_a_larger_local_image`

```python
def test_small_photokit_preview_stays_visible_while_waiting_for_a_larger_local_image(self)
```

<a id="symbol-tests.test_photo_libraries.PhotoLibrariesTests.test_switching_accounts_keeps_old_catalogue_and_copy_associations"></a>

### `PhotoLibrariesTests.test_switching_accounts_keeps_old_catalogue_and_copy_associations`

```python
def test_switching_accounts_keeps_old_catalogue_and_copy_associations(self)
```

<a id="symbol-tests.test_photo_libraries.PhotoLibrariesTests.test_thumbnail_identity_guard_stops_a_changed_library_before_writing"></a>

### `PhotoLibrariesTests.test_thumbnail_identity_guard_stops_a_changed_library_before_writing`

```python
def test_thumbnail_identity_guard_stops_a_changed_library_before_writing(self)
```

<a id="module-tests.test_photos_adapter"></a>

## `test_photos_adapter.py`

NDJSON, Unix-сокет, отмена и границы блоков.

[tests/test_photos_adapter.py](../../tests/test_photos_adapter.py)

<a id="symbol-tests.test_photos_adapter.PhotosAdapterTests.test_consumer_error_closes_only_its_transport_and_rejects_oversized_chunks"></a>

### `PhotosAdapterTests.test_consumer_error_closes_only_its_transport_and_rejects_oversized_chunks`

```python
def test_consumer_error_closes_only_its_transport_and_rejects_oversized_chunks(self)
```

<a id="symbol-tests.test_photos_adapter.PhotosAdapterTests.test_gui_refuses_an_insecure_or_symlinked_ipc_directory"></a>

### `PhotosAdapterTests.test_gui_refuses_an_insecure_or_symlinked_ipc_directory`

```python
def test_gui_refuses_an_insecure_or_symlinked_ipc_directory(self)
```

<a id="symbol-tests.test_photos_adapter.PhotosAdapterTests.test_gui_socket_transport_reuses_the_launched_app_and_keeps_socket_private"></a>

### `PhotosAdapterTests.test_gui_socket_transport_reuses_the_launched_app_and_keeps_socket_private`

```python
def test_gui_socket_transport_reuses_the_launched_app_and_keeps_socket_private(self)
```

<a id="symbol-tests.test_photos_adapter.PhotosAdapterTests.test_missing_photokit_permission_never_falls_back_to_full_image_export"></a>

### `PhotosAdapterTests.test_missing_photokit_permission_never_falls_back_to_full_image_export`

```python
def test_missing_photokit_permission_never_falls_back_to_full_image_export(self)
```

<a id="symbol-tests.test_photos_adapter.PhotosAdapterTests.test_original_stream_decodes_bounded_chunks_and_verifies_protocol_trailer"></a>

### `PhotosAdapterTests.test_original_stream_decodes_bounded_chunks_and_verifies_protocol_trailer`

```python
def test_original_stream_decodes_bounded_chunks_and_verifies_protocol_trailer(self)
```

<a id="symbol-tests.test_photos_adapter.PhotosAdapterTests.test_preview_requests_reuse_one_process_and_do_not_export_an_original"></a>

### `PhotosAdapterTests.test_preview_requests_reuse_one_process_and_do_not_export_an_original`

```python
def test_preview_requests_reuse_one_process_and_do_not_export_an_original(self)
```

<a id="symbol-tests.test_photos_adapter.PhotosAdapterTests.test_stream_cancellation_sends_matching_token_and_stops_consumer"></a>

### `PhotosAdapterTests.test_stream_cancellation_sends_matching_token_and_stops_consumer`

```python
def test_stream_cancellation_sends_matching_token_and_stops_consumer(self)
```

<a id="symbol-tests.test_photos_adapter.PhotosAdapterTests.test_transport_statuses_distinguish_account_change_permission_and_cloud_wait"></a>

### `PhotosAdapterTests.test_transport_statuses_distinguish_account_change_permission_and_cloud_wait`

```python
def test_transport_statuses_distinguish_account_change_permission_and_cloud_wait(self)
```

<a id="module-tests.test_photos_browser"></a>

## `test_photos_browser.py`

Годы/месяцы, страницы и виртуальные ID.

[tests/test_photos_browser.py](../../tests/test_photos_browser.py)

<a id="symbol-tests.test_photos_browser.PhotosBrowserTests.test_empty_and_undated_catalogues_remain_browsable"></a>

### `PhotosBrowserTests.test_empty_and_undated_catalogues_remain_browsable`

```python
def test_empty_and_undated_catalogues_remain_browsable(self)
```

<a id="symbol-tests.test_photos_browser.PhotosBrowserTests.test_offline_catalogue_opens_as_year_month_and_file_without_calling_photos"></a>

### `PhotosBrowserTests.test_offline_catalogue_opens_as_year_month_and_file_without_calling_photos`

```python
def test_offline_catalogue_opens_as_year_month_and_file_without_calling_photos(self)
```

<a id="symbol-tests.test_photos_browser.PhotosBrowserTests.test_pagination_includes_every_object_even_with_duplicate_filenames"></a>

### `PhotosBrowserTests.test_pagination_includes_every_object_even_with_duplicate_filenames`

```python
def test_pagination_includes_every_object_even_with_duplicate_filenames(self)
```

<a id="symbol-tests.test_photos_browser.PhotosBrowserTests.test_paths_and_preview_status_are_scoped_to_the_chosen_library"></a>

### `PhotosBrowserTests.test_paths_and_preview_status_are_scoped_to_the_chosen_library`

```python
def test_paths_and_preview_status_are_scoped_to_the_chosen_library(self)
```

<a id="module-tests.test_photos_copy_chain"></a>

## `test_photos_copy_chain.py`

Источники Photos, квитанции и цепочки копий.

[tests/test_photos_copy_chain.py](../../tests/test_photos_copy_chain.py)

<a id="symbol-tests.test_photos_copy_chain.PhotosCopyChainTests.test_cycle_is_rejected_and_receipts_keep_their_ids_when_renumbered"></a>

### `PhotosCopyChainTests.test_cycle_is_rejected_and_receipts_keep_their_ids_when_renumbered`

```python
def test_cycle_is_rejected_and_receipts_keep_their_ids_when_renumbered(self)
```

<a id="symbol-tests.test_photos_copy_chain.PhotosCopyChainTests.test_existing_hdd_originals_seed_nvme_without_photos_download_or_hdd_rewrite"></a>

### `PhotosCopyChainTests.test_existing_hdd_originals_seed_nvme_without_photos_download_or_hdd_rewrite`

```python
def test_existing_hdd_originals_seed_nvme_without_photos_download_or_hdd_rewrite(self)
```

<a id="symbol-tests.test_photos_copy_chain.PhotosCopyChainTests.test_missing_known_hdd_file_waits_instead_of_redownloading_it"></a>

### `PhotosCopyChainTests.test_missing_known_hdd_file_waits_instead_of_redownloading_it`

```python
def test_missing_known_hdd_file_waits_instead_of_redownloading_it(self)
```

<a id="symbol-tests.test_photos_copy_chain.PhotosCopyChainTests.test_new_original_downloaded_once_then_copied_to_hdd_and_restart_preserves_progress"></a>

### `PhotosCopyChainTests.test_new_original_downloaded_once_then_copied_to_hdd_and_restart_preserves_progress`

```python
def test_new_original_downloaded_once_then_copied_to_hdd_and_restart_preserves_progress(self)
```

<a id="symbol-tests.test_photos_copy_chain.PhotosCopyChainTests.test_offline_second_copy_does_not_redirect_downloads_or_block_first_copy"></a>

### `PhotosCopyChainTests.test_offline_second_copy_does_not_redirect_downloads_or_block_first_copy`

```python
def test_offline_second_copy_does_not_redirect_downloads_or_block_first_copy(self)
```

<a id="symbol-tests.test_photos_copy_chain.PhotosCopyChainTests.test_pause_during_hdd_to_nvme_transfer_recovers_without_network"></a>

### `PhotosCopyChainTests.test_pause_during_hdd_to_nvme_transfer_recovers_without_network`

```python
def test_pause_during_hdd_to_nvme_transfer_recovers_without_network(self)
```

<a id="symbol-tests.test_photos_copy_chain.PhotosCopyChainTests.test_pause_during_replica_inventory_leaves_no_stuck_running_job"></a>

### `PhotosCopyChainTests.test_pause_during_replica_inventory_leaves_no_stuck_running_job`

```python
def test_pause_during_replica_inventory_leaves_no_stuck_running_job(self)
```

<a id="symbol-tests.test_photos_copy_chain.PhotosCopyChainTests.test_replication_happens_before_all_photos_downloads_finish"></a>

### `PhotosCopyChainTests.test_replication_happens_before_all_photos_downloads_finish`

```python
def test_replication_happens_before_all_photos_downloads_finish(self)
```

<a id="symbol-tests.test_photos_copy_chain.PhotosCopyChainTests.test_source_metadata_change_blocks_seed_without_photos_fallback"></a>

### `PhotosCopyChainTests.test_source_metadata_change_blocks_seed_without_photos_fallback`

```python
def test_source_metadata_change_blocks_seed_without_photos_fallback(self)
```

<a id="module-tests.test_photos_originals"></a>

## `test_photos_originals.py`

Прямая запись, версии, продолжение и частичные ресурсы.

[tests/test_photos_originals.py](../../tests/test_photos_originals.py)

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_adopts_manual_copy_by_name_size_and_metadata_and_preserves_name_collision"></a>

### `PhotosOriginalsTests.test_adopts_manual_copy_by_name_size_and_metadata_and_preserves_name_collision`

```python
def test_adopts_manual_copy_by_name_size_and_metadata_and_preserves_name_collision(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_ambiguous_manual_names_are_not_adopted"></a>

### `PhotosOriginalsTests.test_ambiguous_manual_names_are_not_adopted`

```python
def test_ambiguous_manual_names_are_not_adopted(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_changed_existing_original_is_preserved_and_downloaded_to_a_free_name"></a>

### `PhotosOriginalsTests.test_changed_existing_original_is_preserved_and_downloaded_to_a_free_name`

```python
def test_changed_existing_original_is_preserved_and_downloaded_to_a_free_name(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_changed_mtime_even_at_same_size_is_saved_to_a_free_name"></a>

### `PhotosOriginalsTests.test_changed_mtime_even_at_same_size_is_saved_to_a_free_name`

```python
def test_changed_mtime_even_at_same_size_is_saved_to_a_free_name(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_changed_photos_version_does_not_reuse_an_old_receipt_or_overwrite_it"></a>

### `PhotosOriginalsTests.test_changed_photos_version_does_not_reuse_an_old_receipt_or_overwrite_it`

```python
def test_changed_photos_version_does_not_reuse_an_old_receipt_or_overwrite_it(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_changed_written_size_never_creates_a_receipt"></a>

### `PhotosOriginalsTests.test_changed_written_size_never_creates_a_receipt`

```python
def test_changed_written_size_never_creates_a_receipt(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_chunks_are_combined_into_bounded_blocks_and_tail_is_flushed_once"></a>

### `PhotosOriginalsTests.test_chunks_are_combined_into_bounded_blocks_and_tail_is_flushed_once`

```python
def test_chunks_are_combined_into_bounded_blocks_and_tail_is_flushed_once(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_copy_writes_once_without_rename_readback_or_temporary_media"></a>

### `PhotosOriginalsTests.test_copy_writes_once_without_rename_readback_or_temporary_media`

```python
def test_copy_writes_once_without_rename_readback_or_temporary_media(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_disk_full_does_not_publish_or_count_an_original"></a>

### `PhotosOriginalsTests.test_disk_full_does_not_publish_or_count_an_original`

```python
def test_disk_full_does_not_publish_or_count_an_original(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_file_appearing_before_exclusive_creation_is_never_replaced"></a>

### `PhotosOriginalsTests.test_file_appearing_before_exclusive_creation_is_never_replaced`

```python
def test_file_appearing_before_exclusive_creation_is_never_replaced(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_first_and_second_runs_never_read_media_for_verification"></a>

### `PhotosOriginalsTests.test_first_and_second_runs_never_read_media_for_verification`

```python
def test_first_and_second_runs_never_read_media_for_verification(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_fsync_failure_is_journalled_even_when_size_matches"></a>

### `PhotosOriginalsTests.test_fsync_failure_is_journalled_even_when_size_matches`

```python
def test_fsync_failure_is_journalled_even_when_size_matches(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_interrupted_smb_final_is_preserved_and_reported_on_retry"></a>

### `PhotosOriginalsTests.test_interrupted_smb_final_is_preserved_and_reported_on_retry`

```python
def test_interrupted_smb_final_is_preserved_and_reported_on_retry(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_legacy_reset_manifest_recovers_all_receipts_before_resume"></a>

### `PhotosOriginalsTests.test_legacy_reset_manifest_recovers_all_receipts_before_resume`

```python
def test_legacy_reset_manifest_recovers_all_receipts_before_resume(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_manual_file_changed_after_inventory_is_not_adopted"></a>

### `PhotosOriginalsTests.test_manual_file_changed_after_inventory_is_not_adopted`

```python
def test_manual_file_changed_after_inventory_is_not_adopted(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_metadata_preserving_changes_are_not_read_or_content_compared"></a>

### `PhotosOriginalsTests.test_metadata_preserving_changes_are_not_read_or_content_compared`

```python
def test_metadata_preserving_changes_are_not_read_or_content_compared(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_missing_receipt_file_is_downloaded_again_without_rereading_other_files"></a>

### `PhotosOriginalsTests.test_missing_receipt_file_is_downloaded_again_without_rereading_other_files`

```python
def test_missing_receipt_file_is_downloaded_again_without_rereading_other_files(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_original_worker_closes_every_database_connection"></a>

### `PhotosOriginalsTests.test_original_worker_closes_every_database_connection`

```python
def test_original_worker_closes_every_database_connection(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_pause_after_one_block_preserves_partial_file_and_resume_uses_free_name"></a>

### `PhotosOriginalsTests.test_pause_after_one_block_preserves_partial_file_and_resume_uses_free_name`

```python
def test_pause_after_one_block_preserves_partial_file_and_resume_uses_free_name(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_pause_before_buffer_flush_creates_no_incomplete_file"></a>

### `PhotosOriginalsTests.test_pause_before_buffer_flush_creates_no_incomplete_file`

```python
def test_pause_before_buffer_flush_creates_no_incomplete_file(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_pause_mid_stream_and_resume_preserve_finished_resources"></a>

### `PhotosOriginalsTests.test_pause_mid_stream_and_resume_preserve_finished_resources`

```python
def test_pause_mid_stream_and_resume_preserve_finished_resources(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_replaced_root_is_rejected_on_resume"></a>

### `PhotosOriginalsTests.test_replaced_root_is_rejected_on_resume`

```python
def test_replaced_root_is_rejected_on_resume(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_restart_turns_active_job_into_resumable_pause"></a>

### `PhotosOriginalsTests.test_restart_turns_active_job_into_resumable_pause`

```python
def test_restart_turns_active_job_into_resumable_pause(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_resume_keeps_progress_during_inventory_and_partial_manifest"></a>

### `PhotosOriginalsTests.test_resume_keeps_progress_during_inventory_and_partial_manifest`

```python
def test_resume_keeps_progress_during_inventory_and_partial_manifest(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_short_os_writes_still_save_every_byte"></a>

### `PhotosOriginalsTests.test_short_os_writes_still_save_every_byte`

```python
def test_short_os_writes_still_save_every_byte(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_stream_size_mismatch_never_creates_receipts_or_completed_assets"></a>

### `PhotosOriginalsTests.test_stream_size_mismatch_never_creates_receipts_or_completed_assets`

```python
def test_stream_size_mismatch_never_creates_receipts_or_completed_assets(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_streams_all_live_photo_resources_and_keeps_only_metadata_in_database"></a>

### `PhotosOriginalsTests.test_streams_all_live_photo_resources_and_keeps_only_metadata_in_database`

```python
def test_streams_all_live_photo_resources_and_keeps_only_metadata_in_database(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_symlinked_destination_cannot_escape_the_bound_copy"></a>

### `PhotosOriginalsTests.test_symlinked_destination_cannot_escape_the_bound_copy`

```python
def test_symlinked_destination_cannot_escape_the_bound_copy(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_unbinding_or_account_change_stops_before_any_final_file"></a>

### `PhotosOriginalsTests.test_unbinding_or_account_change_stops_before_any_final_file`

```python
def test_unbinding_or_account_change_stops_before_any_final_file(self)
```

<a id="symbol-tests.test_photos_originals.PhotosOriginalsTests.test_unknown_staging_file_is_never_deleted"></a>

### `PhotosOriginalsTests.test_unknown_staging_file_is_never_deleted`

```python
def test_unknown_staging_file_is_never_deleted(self)
```

<a id="module-tests.test_photos_schedule"></a>

## `test_photos_schedule.py`

Окна времени, повторные запросы и ручная пауза.

[tests/test_photos_schedule.py](../../tests/test_photos_schedule.py)

<a id="symbol-tests.test_photos_schedule.PhotosScheduleTests.test_daytime_enable_defers_started_work_and_disabling_allows_continuation"></a>

### `PhotosScheduleTests.test_daytime_enable_defers_started_work_and_disabling_allows_continuation`

```python
def test_daytime_enable_defers_started_work_and_disabling_allows_continuation(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosScheduleTests.test_daytime_request_is_queued_without_opening_or_scanning_the_copy"></a>

### `PhotosScheduleTests.test_daytime_request_is_queued_without_opening_or_scanning_the_copy`

```python
def test_daytime_request_is_queued_without_opening_or_scanning_the_copy(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosScheduleTests.test_inactive_window_does_not_pause_ordinary_folder_previews"></a>

### `PhotosScheduleTests.test_inactive_window_does_not_pause_ordinary_folder_previews`

```python
def test_inactive_window_does_not_pause_ordinary_folder_previews(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosScheduleTests.test_interrupted_night_run_resumes_after_restart_within_the_same_window"></a>

### `PhotosScheduleTests.test_interrupted_night_run_resumes_after_restart_within_the_same_window`

```python
def test_interrupted_night_run_resumes_after_restart_within_the_same_window(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosScheduleTests.test_invalid_windows_are_rejected_without_changing_the_policy"></a>

### `PhotosScheduleTests.test_invalid_windows_are_rejected_without_changing_the_policy`

```python
def test_invalid_windows_are_rejected_without_changing_the_policy(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosScheduleTests.test_manual_pause_cancels_automatic_resume_even_after_changing_hours"></a>

### `PhotosScheduleTests.test_manual_pause_cancels_automatic_resume_even_after_changing_hours`

```python
def test_manual_pause_cancels_automatic_resume_even_after_changing_hours(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosScheduleTests.test_manual_preview_pause_survives_the_night_window"></a>

### `PhotosScheduleTests.test_manual_preview_pause_survives_the_night_window`

```python
def test_manual_preview_pause_survives_the_night_window(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosScheduleTests.test_schedule_api_persists_window_and_original_start_respects_it"></a>

### `PhotosScheduleTests.test_schedule_api_persists_window_and_original_start_respects_it`

```python
def test_schedule_api_persists_window_and_original_start_respects_it(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosScheduleTests.test_scheduler_starts_at_midnight_and_does_not_repeat_a_finished_run"></a>

### `PhotosScheduleTests.test_scheduler_starts_at_midnight_and_does_not_repeat_a_finished_run`

```python
def test_scheduler_starts_at_midnight_and_does_not_repeat_a_finished_run(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosScheduleTests.test_settings_and_queued_requests_survive_a_core_restart"></a>

### `PhotosScheduleTests.test_settings_and_queued_requests_survive_a_core_restart`

```python
def test_settings_and_queued_requests_survive_a_core_restart(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosScheduleTests.test_source_card_distinguishes_manual_pause_and_waiting_for_night"></a>

### `PhotosScheduleTests.test_source_card_distinguishes_manual_pause_and_waiting_for_night`

```python
def test_source_card_distinguishes_manual_pause_and_waiting_for_night(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosScheduleTests.test_thumbnail_claims_scan_and_new_thumbnail_generation_wait_for_night"></a>

### `PhotosScheduleTests.test_thumbnail_claims_scan_and_new_thumbnail_generation_wait_for_night`

```python
def test_thumbnail_claims_scan_and_new_thumbnail_generation_wait_for_night(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosScheduleTests.test_unbound_copy_or_another_account_cannot_start_from_the_timer"></a>

### `PhotosScheduleTests.test_unbound_copy_or_another_account_cannot_start_from_the_timer`

```python
def test_unbound_copy_or_another_account_cannot_start_from_the_timer(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosScheduleTests.test_window_end_cancels_current_resource_and_resumes_the_next_night"></a>

### `PhotosScheduleTests.test_window_end_cancels_current_resource_and_resumes_the_next_night`

```python
def test_window_end_cancels_current_resource_and_resumes_the_next_night(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosWindowTests.test_moscow_window_uses_local_time_and_exact_boundaries"></a>

### `PhotosWindowTests.test_moscow_window_uses_local_time_and_exact_boundaries`

```python
def test_moscow_window_uses_local_time_and_exact_boundaries(self)
```

<a id="symbol-tests.test_photos_schedule.PhotosWindowTests.test_window_crossing_midnight_has_one_daily_identity"></a>

### `PhotosWindowTests.test_window_crossing_midnight_has_one_daily_identity`

```python
def test_window_crossing_midnight_has_one_daily_identity(self)
```

<a id="module-tests.test_refresh_renamed_folder"></a>

## `test_refresh_renamed_folder.py`

Обновление переименованной области UI.

[tests/test_refresh_renamed_folder.py](../../tests/test_refresh_renamed_folder.py)

<a id="symbol-tests.test_refresh_renamed_folder.RefreshRenamedFolderTests.test_a_renamed_browser_root_falls_back_to_a_readable_parent"></a>

### `RefreshRenamedFolderTests.test_a_renamed_browser_root_falls_back_to_a_readable_parent`

```python
async def test_a_renamed_browser_root_falls_back_to_a_readable_parent(self)
```

<a id="symbol-tests.test_refresh_renamed_folder.RefreshRenamedFolderTests.test_a_renamed_file_clears_old_selection_and_updates_the_list"></a>

### `RefreshRenamedFolderTests.test_a_renamed_file_clears_old_selection_and_updates_the_list`

```python
async def test_a_renamed_file_clears_old_selection_and_updates_the_list(self)
```

<a id="symbol-tests.test_refresh_renamed_folder.RefreshRenamedFolderTests.test_permissions_failure_keeps_cached_entries_and_does_not_claim_the_folder_disappeared"></a>

### `RefreshRenamedFolderTests.test_permissions_failure_keeps_cached_entries_and_does_not_claim_the_folder_disappeared`

```python
async def test_permissions_failure_keeps_cached_entries_and_does_not_claim_the_folder_disappeared(self)
```

<a id="symbol-tests.test_refresh_renamed_folder.RefreshRenamedFolderTests.test_refresh_of_an_existing_folder_also_updates_its_parent_listing"></a>

### `RefreshRenamedFolderTests.test_refresh_of_an_existing_folder_also_updates_its_parent_listing`

```python
async def test_refresh_of_an_existing_folder_also_updates_its_parent_listing(self)
```

<a id="symbol-tests.test_refresh_renamed_folder.RefreshRenamedFolderTests.test_refresh_shows_new_names_and_leaves_the_missing_selection_at_its_parent"></a>

### `RefreshRenamedFolderTests.test_refresh_shows_new_names_and_leaves_the_missing_selection_at_its_parent`

```python
async def test_refresh_shows_new_names_and_leaves_the_missing_selection_at_its_parent(self)
```

<a id="symbol-tests.test_refresh_renamed_folder.RefreshRenamedFolderTests.test_renamed_nested_parent_falls_back_to_nearest_existing_ancestor"></a>

### `RefreshRenamedFolderTests.test_renamed_nested_parent_falls_back_to_nearest_existing_ancestor`

```python
async def test_renamed_nested_parent_falls_back_to_nearest_existing_ancestor(self)
```

<a id="module-tests.test_scanner"></a>

## `test_scanner.py`

Рекурсивный обход и ошибки обычного источника.

[tests/test_scanner.py](../../tests/test_scanner.py)

<a id="symbol-tests.test_scanner.ScannerTests.test_does_not_follow_symbolic_links"></a>

### `ScannerTests.test_does_not_follow_symbolic_links`

```python
def test_does_not_follow_symbolic_links(self)
```

<a id="symbol-tests.test_scanner.ScannerTests.test_ignores_macos_metadata_files_and_directories"></a>

### `ScannerTests.test_ignores_macos_metadata_files_and_directories`

```python
def test_ignores_macos_metadata_files_and_directories(self)
```

<a id="symbol-tests.test_scanner.ScannerTests.test_scans_nested_media_and_ignores_other_files"></a>

### `ScannerTests.test_scans_nested_media_and_ignores_other_files`

```python
def test_scans_nested_media_and_ignores_other_files(self)
```

<a id="module-tests.test_service_runtime"></a>

## `test_service_runtime.py`

Ротация журналов и отказ потока.

[tests/test_service_runtime.py](../../tests/test_service_runtime.py)

<a id="symbol-tests.test_service_runtime.ServiceRuntimeTests.test_failed_log_write_does_not_recurse_into_stderr"></a>

### `ServiceRuntimeTests.test_failed_log_write_does_not_recurse_into_stderr`

```python
def test_failed_log_write_does_not_recurse_into_stderr(self)
```

<a id="symbol-tests.test_service_runtime.ServiceRuntimeTests.test_large_stdout_and_stderr_do_not_block_the_launcher_pipe"></a>

### `ServiceRuntimeTests.test_large_stdout_and_stderr_do_not_block_the_launcher_pipe`

```python
def test_large_stdout_and_stderr_do_not_block_the_launcher_pipe(self)
```

<a id="symbol-tests.test_service_runtime.ServiceRuntimeTests.test_logs_rotate_and_keep_utf8_text"></a>

### `ServiceRuntimeTests.test_logs_rotate_and_keep_utf8_text`

```python
def test_logs_rotate_and_keep_utf8_text(self)
```

<a id="symbol-tests.test_service_runtime.ServiceRuntimeTests.test_module_arguments_still_work"></a>

### `ServiceRuntimeTests.test_module_arguments_still_work`

```python
def test_module_arguments_still_work(self)
```

<a id="module-tests.test_sidebar_state"></a>

## `test_sidebar_state.py`

Сохранение раскрытия боковых секций.

[tests/test_sidebar_state.py](../../tests/test_sidebar_state.py)

<a id="symbol-tests.test_sidebar_state.SidebarRefreshTests.test_loading_or_polling_copy_groups_never_toggles_volumes"></a>

### `SidebarRefreshTests.test_loading_or_polling_copy_groups_never_toggles_volumes`

```python
async def test_loading_or_polling_copy_groups_never_toggles_volumes(self)
```

<a id="symbol-tests.test_sidebar_state.SidebarStateTests.test_another_tab_changing_one_section_preserves_the_others"></a>

### `SidebarStateTests.test_another_tab_changing_one_section_preserves_the_others`

```python
def test_another_tab_changing_one_section_preserves_the_others(self)
```

<a id="symbol-tests.test_sidebar_state.SidebarStateTests.test_browser_state_survives_new_page_and_storage_reload"></a>

### `SidebarStateTests.test_browser_state_survives_new_page_and_storage_reload`

```python
def test_browser_state_survives_new_page_and_storage_reload(self)
```

<a id="symbol-tests.test_sidebar_state.SidebarStateTests.test_first_page_has_stable_defaults_without_creating_preferences"></a>

### `SidebarStateTests.test_first_page_has_stable_defaults_without_creating_preferences`

```python
def test_first_page_has_stable_defaults_without_creating_preferences(self)
```

<a id="symbol-tests.test_sidebar_state.SidebarStateTests.test_invalid_preferences_do_not_expand_or_hide_unrelated_sections"></a>

### `SidebarStateTests.test_invalid_preferences_do_not_expand_or_hide_unrelated_sections`

```python
def test_invalid_preferences_do_not_expand_or_hide_unrelated_sections(self)
```

<a id="module-tests.test_storage"></a>

## `test_storage.py`

Снимки, отключение и метаданные томов.

[tests/test_storage.py](../../tests/test_storage.py)

<a id="symbol-tests.test_storage.StorageTests.test_cached_directory_does_not_wait_for_mount_discovery"></a>

### `StorageTests.test_cached_directory_does_not_wait_for_mount_discovery`

```python
def test_cached_directory_does_not_wait_for_mount_discovery(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_directory_refresh_rechecks_identity_even_within_discovery_cache"></a>

### `StorageTests.test_directory_refresh_rechecks_identity_even_within_discovery_cache`

```python
def test_directory_refresh_rechecks_identity_even_within_discovery_cache(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_disconnected_tree_and_roles_survive_restart"></a>

### `StorageTests.test_disconnected_tree_and_roles_survive_restart`

```python
def test_disconnected_tree_and_roles_survive_restart(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_discovery_failure_is_unknown_not_offline"></a>

### `StorageTests.test_discovery_failure_is_unknown_not_offline`

```python
def test_discovery_failure_is_unknown_not_offline(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_finder_opens_volumes_and_folders_and_reveals_files_and_links"></a>

### `StorageTests.test_finder_opens_volumes_and_folders_and_reveals_files_and_links`

```python
def test_finder_opens_volumes_and_folders_and_reveals_files_and_links(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_finder_rechecks_volume_identity_and_availability_before_opening"></a>

### `StorageTests.test_finder_rechecks_volume_identity_and_availability_before_opening`

```python
def test_finder_rechecks_volume_identity_and_availability_before_opening(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_finder_rejects_missing_entries_traversal_and_symlink_parents"></a>

### `StorageTests.test_finder_rejects_missing_entries_traversal_and_symlink_parents`

```python
def test_finder_rejects_missing_entries_traversal_and_symlink_parents(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_finder_reports_launch_failure_and_timeout"></a>

### `StorageTests.test_finder_reports_launch_failure_and_timeout`

```python
def test_finder_reports_launch_failure_and_timeout(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_lists_all_types_and_empty_directories_without_writing_originals"></a>

### `StorageTests.test_lists_all_types_and_empty_directories_without_writing_originals`

```python
def test_lists_all_types_and_empty_directories_without_writing_originals(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_mount_replaced_between_discovery_and_open_preserves_snapshot"></a>

### `StorageTests.test_mount_replaced_between_discovery_and_open_preserves_snapshot`

```python
def test_mount_replaced_between_discovery_and_open_preserves_snapshot(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_network_identity_ignores_username_and_mount_point"></a>

### `StorageTests.test_network_identity_ignores_username_and_mount_point`

```python
def test_network_identity_ignores_username_and_mount_point(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_new_disk_at_same_mount_path_does_not_inherit_roles_or_snapshots"></a>

### `StorageTests.test_new_disk_at_same_mount_path_does_not_inherit_roles_or_snapshots`

```python
def test_new_disk_at_same_mount_path_does_not_inherit_roles_or_snapshots(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_read_failure_preserves_last_successful_snapshot"></a>

### `StorageTests.test_read_failure_preserves_last_successful_snapshot`

```python
def test_read_failure_preserves_last_successful_snapshot(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_rejects_traversal_symlinks_and_roles_for_arbitrary_paths"></a>

### `StorageTests.test_rejects_traversal_symlinks_and_roles_for_arbitrary_paths`

```python
def test_rejects_traversal_symlinks_and_roles_for_arbitrary_paths(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_removed_share_archives_without_breaking_other_volumes_and_can_return"></a>

### `StorageTests.test_removed_share_archives_without_breaking_other_volumes_and_can_return`

```python
def test_removed_share_archives_without_breaking_other_volumes_and_can_return(self)
```

<a id="symbol-tests.test_storage.StorageTests.test_roles_inherit_and_can_be_cleared_or_overridden"></a>

### `StorageTests.test_roles_inherit_and_can_be_cleared_or_overridden`

```python
def test_roles_inherit_and_can_be_cleared_or_overridden(self)
```

<a id="module-tests.test_storage_previews"></a>

## `test_storage_previews.py`

Производные JPEG, видео и режим превью.

[tests/test_storage_previews.py](../../tests/test_storage_previews.py)

<a id="symbol-tests.test_storage_previews.PreviewNavigationTests.test_modes_restore_without_changing_saved_tree_position"></a>

### `PreviewNavigationTests.test_modes_restore_without_changing_saved_tree_position`

```python
async def test_modes_restore_without_changing_saved_tree_position(self)
```

<a id="symbol-tests.test_storage_previews.PreviewNavigationTests.test_only_opposite_preview_receives_selection_and_keeps_its_tree_state"></a>

### `PreviewNavigationTests.test_only_opposite_preview_receives_selection_and_keeps_its_tree_state`

```python
async def test_only_opposite_preview_receives_selection_and_keeps_its_tree_state(self)
```

<a id="symbol-tests.test_storage_previews.PreviewNavigationTests.test_preview_path_is_saved_separately_and_validated"></a>

### `PreviewNavigationTests.test_preview_path_is_saved_separately_and_validated`

```python
def test_preview_path_is_saved_separately_and_validated(self)
```

<a id="symbol-tests.test_storage_previews.PreviewNavigationTests.test_slow_folder_response_cannot_replace_a_newer_file_selection"></a>

### `PreviewNavigationTests.test_slow_folder_response_cannot_replace_a_newer_file_selection`

```python
async def test_slow_folder_response_cannot_replace_a_newer_file_selection(self)
```

<a id="symbol-tests.test_storage_previews.StoragePreviewTests.test_absolute_paths_parent_traversal_symlinks_and_fifos_are_refused"></a>

### `StoragePreviewTests.test_absolute_paths_parent_traversal_symlinks_and_fifos_are_refused`

```python
def test_absolute_paths_parent_traversal_symlinks_and_fifos_are_refused(self)
```

<a id="symbol-tests.test_storage_previews.StoragePreviewTests.test_derivatives_have_two_sizes_reuse_cache_and_leave_original_unchanged"></a>

### `StoragePreviewTests.test_derivatives_have_two_sizes_reuse_cache_and_leave_original_unchanged`

```python
def test_derivatives_have_two_sizes_reuse_cache_and_leave_original_unchanged(self)
```

<a id="symbol-tests.test_storage_previews.StoragePreviewTests.test_offline_or_replaced_disk_is_not_read_even_when_a_derivative_exists"></a>

### `StoragePreviewTests.test_offline_or_replaced_disk_is_not_read_even_when_a_derivative_exists`

```python
def test_offline_or_replaced_disk_is_not_read_even_when_a_derivative_exists(self)
```

<a id="symbol-tests.test_storage_previews.StoragePreviewTests.test_replacement_invalidates_cache_and_tiles_do_not_discover_all_disks"></a>

### `StoragePreviewTests.test_replacement_invalidates_cache_and_tiles_do_not_discover_all_disks`

```python
def test_replacement_invalidates_cache_and_tiles_do_not_discover_all_disks(self)
```

<a id="symbol-tests.test_storage_previews.StoragePreviewTests.test_video_frame_from_checked_descriptor_and_macos_fallback"></a>

### `StoragePreviewTests.test_video_frame_from_checked_descriptor_and_macos_fallback`

```python
def test_video_frame_from_checked_descriptor_and_macos_fallback(self)
```

<a id="module-tests.test_thumbnails"></a>

## `test_thumbnails.py`

Версии кэша, ориентация и генерация фото.

[tests/test_thumbnails.py](../../tests/test_thumbnails.py)

<a id="symbol-tests.test_thumbnails.ThumbnailTests.test_missing_external_cache_does_not_fall_back_to_system_disk"></a>

### `ThumbnailTests.test_missing_external_cache_does_not_fall_back_to_system_disk`

```python
def test_missing_external_cache_does_not_fall_back_to_system_disk(self)
```

<a id="symbol-tests.test_thumbnails.ThumbnailTests.test_reused_media_id_does_not_reuse_another_files_thumbnail"></a>

### `ThumbnailTests.test_reused_media_id_does_not_reuse_another_files_thumbnail`

```python
def test_reused_media_id_does_not_reuse_another_files_thumbnail(self)
```

<a id="symbol-tests.test_thumbnails.ThumbnailTests.test_thumbnail_is_written_only_to_cache"></a>

### `ThumbnailTests.test_thumbnail_is_written_only_to_cache`

```python
def test_thumbnail_is_written_only_to_cache(self)
```

<a id="module-tests.test_tree_keyboard"></a>

## `test_tree_keyboard.py`

Выделение, фокус и клавиатурная навигация.

[tests/test_tree_keyboard.py](../../tests/test_tree_keyboard.py)

<a id="symbol-tests.test_tree_keyboard.TreeKeyboardJavaScriptTests.test_rendered_rows_boundaries_inputs_and_new_render_revision"></a>

### `TreeKeyboardJavaScriptTests.test_rendered_rows_boundaries_inputs_and_new_render_revision`

```python
def test_rendered_rows_boundaries_inputs_and_new_render_revision(self)
```

<a id="symbol-tests.test_tree_keyboard.TreeKeyboardJavaScriptTests.test_virtual_tree_moves_beyond_the_viewport_and_ignores_old_server_selection"></a>

### `TreeKeyboardJavaScriptTests.test_virtual_tree_moves_beyond_the_viewport_and_ignores_old_server_selection`

```python
def test_virtual_tree_moves_beyond_the_viewport_and_ignores_old_server_selection(self)
```

<a id="symbol-tests.test_tree_keyboard.TreeKeyboardTests.test_arrow_selection_does_not_toggle_or_rebuild_a_folder"></a>

### `TreeKeyboardTests.test_arrow_selection_does_not_toggle_or_rebuild_a_folder`

```python
async def test_arrow_selection_does_not_toggle_or_rebuild_a_folder(self)
```

<a id="symbol-tests.test_tree_keyboard.TreeKeyboardTests.test_comparison_arrow_selection_preserves_collapsed_folders"></a>

### `TreeKeyboardTests.test_comparison_arrow_selection_preserves_collapsed_folders`

```python
async def test_comparison_arrow_selection_preserves_collapsed_folders(self)
```

<a id="symbol-tests.test_tree_keyboard.TreeKeyboardTests.test_disconnected_sources_are_hidden_but_the_current_caption_is_preserved"></a>

### `TreeKeyboardTests.test_disconnected_sources_are_hidden_but_the_current_caption_is_preserved`

```python
async def test_disconnected_sources_are_hidden_but_the_current_caption_is_preserved(self)
```

<a id="symbol-tests.test_tree_keyboard.TreeKeyboardTests.test_paired_arrow_keeps_a_collapsed_folder_closed_and_updates_both_sides"></a>

### `TreeKeyboardTests.test_paired_arrow_keeps_a_collapsed_folder_closed_and_updates_both_sides`

```python
async def test_paired_arrow_keeps_a_collapsed_folder_closed_and_updates_both_sides(self)
```

<a id="symbol-tests.test_tree_keyboard.TreeKeyboardTests.test_stale_events_and_dialog_or_preview_focus_do_not_move_the_tree"></a>

### `TreeKeyboardTests.test_stale_events_and_dialog_or_preview_focus_do_not_move_the_tree`

```python
async def test_stale_events_and_dialog_or_preview_focus_do_not_move_the_tree(self)
```

<a id="module-tests.test_ui_connection"></a>

## `test_ui_connection.py`

Повторное использование HTTP-пула.

[tests/test_ui_connection.py](../../tests/test_ui_connection.py)

<a id="symbol-tests.test_ui_connection.UIConnectionTests.test_core_polling_reuses_a_connection_pool_and_closes_it_on_shutdown"></a>

### `UIConnectionTests.test_core_polling_reuses_a_connection_pool_and_closes_it_on_shutdown`

```python
async def test_core_polling_reuses_a_connection_pool_and_closes_it_on_shutdown(self)
```

<a id="module-tests.test_volume_identity"></a>

## `test_volume_identity.py`

Маркеры, смена носителя и ёмкость.

[tests/test_volume_identity.py](../../tests/test_volume_identity.py)

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_capacity_keeps_last_successful_measurement_offline_and_on_failure"></a>

### `VolumeIdentityTests.test_capacity_keeps_last_successful_measurement_offline_and_on_failure`

```python
def test_capacity_keeps_last_successful_measurement_offline_and_on_failure(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_capacity_uses_all_free_blocks_and_reports_user_available_separately"></a>

### `VolumeIdentityTests.test_capacity_uses_all_free_blocks_and_reports_user_available_separately`

```python
def test_capacity_uses_all_free_blocks_and_reports_user_available_separately(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_concurrent_marker_change_is_not_overwritten"></a>

### `VolumeIdentityTests.test_concurrent_marker_change_is_not_overwritten`

```python
def test_concurrent_marker_change_is_not_overwritten(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_duplicate_markers_block_both_mounts"></a>

### `VolumeIdentityTests.test_duplicate_markers_block_both_mounts`

```python
def test_duplicate_markers_block_both_mounts(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_failed_rename_leaves_original_marker_intact_and_removes_temporary"></a>

### `VolumeIdentityTests.test_failed_rename_leaves_original_marker_intact_and_removes_temporary`

```python
def test_failed_rename_leaves_original_marker_intact_and_removes_temporary(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_identity_rechecked_before_and_after_directory_read"></a>

### `VolumeIdentityTests.test_identity_rechecked_before_and_after_directory_read`

```python
def test_identity_rechecked_before_and_after_directory_read(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_invalid_oversized_or_special_marker_never_becomes_verified"></a>

### `VolumeIdentityTests.test_invalid_oversized_or_special_marker_never_becomes_verified`

```python
def test_invalid_oversized_or_special_marker_never_becomes_verified(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_marker_is_excluded_from_comparison_inventory"></a>

### `VolumeIdentityTests.test_marker_is_excluded_from_comparison_inventory`

```python
def test_marker_is_excluded_from_comparison_inventory(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_other_disk_at_same_share_cannot_inherit_history"></a>

### `VolumeIdentityTests.test_other_disk_at_same_share_cannot_inherit_history`

```python
def test_other_disk_at_same_share_cannot_inherit_history(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_registration_refuses_existing_file_and_symlink_without_overwrite"></a>

### `VolumeIdentityTests.test_registration_refuses_existing_file_and_symlink_without_overwrite`

```python
def test_registration_refuses_existing_file_and_symlink_without_overwrite(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_registration_writes_only_marker_and_survives_share_alias_restart"></a>

### `VolumeIdentityTests.test_registration_writes_only_marker_and_survives_share_alias_restart`

```python
def test_registration_writes_only_marker_and_survives_share_alias_restart(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_remembered_usb_resource_does_not_alias_legacy_disk"></a>

### `VolumeIdentityTests.test_remembered_usb_resource_does_not_alias_legacy_disk`

```python
def test_remembered_usb_resource_does_not_alias_legacy_disk(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_rename_api_validates_requests_and_updates_the_same_volume"></a>

### `VolumeIdentityTests.test_rename_api_validates_requests_and_updates_the_same_volume`

```python
def test_rename_api_validates_requests_and_updates_the_same_volume(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_rename_preserves_marker_history_and_folder_connections_after_restart"></a>

### `VolumeIdentityTests.test_rename_preserves_marker_history_and_folder_connections_after_restart`

```python
def test_rename_preserves_marker_history_and_folder_connections_after_restart(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_rename_rejects_changed_identity_symlink_and_invalid_names"></a>

### `VolumeIdentityTests.test_rename_rejects_changed_identity_symlink_and_invalid_names`

```python
def test_rename_rejects_changed_identity_symlink_and_invalid_names(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_rename_rejects_offline_unregistered_and_duplicate_disks"></a>

### `VolumeIdentityTests.test_rename_rejects_offline_unregistered_and_duplicate_disks`

```python
def test_rename_rejects_offline_unregistered_and_duplicate_disks(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_swap_during_read_rejects_result"></a>

### `VolumeIdentityTests.test_swap_during_read_rejects_result`

```python
def test_swap_during_read_rejects_result(self)
```

<a id="symbol-tests.test_volume_identity.VolumeIdentityTests.test_unregistered_disk_does_not_use_legacy_share_history"></a>

### `VolumeIdentityTests.test_unregistered_disk_does_not_use_legacy_share_history`

```python
def test_unregistered_disk_does_not_use_legacy_share_history(self)
```

<a id="module-tests.test_workspace_photos"></a>

## `test_workspace_photos.py`

Виртуальные медиатеки в общих панелях.

[tests/test_workspace_photos.py](../../tests/test_workspace_photos.py)

<a id="symbol-tests.test_workspace_photos.WorkspacePhotosTests.test_library_button_opens_the_active_tree_without_changing_preview_mode"></a>

### `WorkspacePhotosTests.test_library_button_opens_the_active_tree_without_changing_preview_mode`

```python
async def test_library_button_opens_the_active_tree_without_changing_preview_mode(self)
```

<a id="symbol-tests.test_workspace_photos.WorkspacePhotosTests.test_photos_browse_never_uses_mounted_directory_or_comparison_apis"></a>

### `WorkspacePhotosTests.test_photos_browse_never_uses_mounted_directory_or_comparison_apis`

```python
async def test_photos_browse_never_uses_mounted_directory_or_comparison_apis(self)
```

<a id="module-tests.test_workspace_refresh"></a>

## `test_workspace_refresh.py`

Обновление UI без потери дерева.

[tests/test_workspace_refresh.py](../../tests/test_workspace_refresh.py)

<a id="symbol-tests.test_workspace_refresh.WorkspaceRefreshTests.test_background_polling_stops_until_the_same_client_reconnects"></a>

### `WorkspaceRefreshTests.test_background_polling_stops_until_the_same_client_reconnects`

```python
async def test_background_polling_stops_until_the_same_client_reconnects(self)
```

<a id="symbol-tests.test_workspace_refresh.WorkspaceRefreshTests.test_capacity_poll_preserves_existing_disk_and_photos_trees"></a>

### `WorkspaceRefreshTests.test_capacity_poll_preserves_existing_disk_and_photos_trees`

```python
async def test_capacity_poll_preserves_existing_disk_and_photos_trees(self)
```

<a id="symbol-tests.test_workspace_refresh.WorkspaceRefreshTests.test_explicit_volume_refresh_can_redraw_both_trees"></a>

### `WorkspaceRefreshTests.test_explicit_volume_refresh_can_redraw_both_trees`

```python
async def test_explicit_volume_refresh_can_redraw_both_trees(self)
```

<a id="symbol-tests.test_workspace_refresh.WorkspaceRefreshTests.test_volume_access_change_updates_only_the_affected_tree"></a>

### `WorkspaceRefreshTests.test_volume_access_change_updates_only_the_affected_tree`

```python
async def test_volume_access_change_updates_only_the_affected_tree(self)
```

<a id="module-tests.test_workspace_state"></a>

## `test_workspace_state.py`

Нормализация и восстановление состояния вкладки.

[tests/test_workspace_state.py](../../tests/test_workspace_state.py)

<a id="symbol-tests.test_workspace_state.PairProgressViewTests.test_polling_the_same_running_report_preserves_both_paths_and_file_selection"></a>

### `PairProgressViewTests.test_polling_the_same_running_report_preserves_both_paths_and_file_selection`

```python
async def test_polling_the_same_running_report_preserves_both_paths_and_file_selection(self)
```

<a id="symbol-tests.test_workspace_state.PairProgressViewTests.test_restored_navigation_waits_for_rows_without_changing_the_report"></a>

### `PairProgressViewTests.test_restored_navigation_waits_for_rows_without_changing_the_report`

```python
async def test_restored_navigation_waits_for_rows_without_changing_the_report(self)
```

<a id="symbol-tests.test_workspace_state.WorkspaceRestoreTests.test_plain_panels_restore_both_roots_and_the_selected_file"></a>

### `WorkspaceRestoreTests.test_plain_panels_restore_both_roots_and_the_selected_file`

```python
async def test_plain_panels_restore_both_roots_and_the_selected_file(self)
```

<a id="symbol-tests.test_workspace_state.WorkspaceRestoreTests.test_reload_during_create_response_recovers_the_created_job_once"></a>

### `WorkspaceRestoreTests.test_reload_during_create_response_recovers_the_created_job_once`

```python
async def test_reload_during_create_response_recovers_the_created_job_once(self)
```

<a id="symbol-tests.test_workspace_state.WorkspaceRestoreTests.test_running_report_is_read_without_starting_resuming_or_pausing_a_job"></a>

### `WorkspaceRestoreTests.test_running_report_is_read_without_starting_resuming_or_pausing_a_job`

```python
async def test_running_report_is_read_without_starting_resuming_or_pausing_a_job(self)
```

<a id="symbol-tests.test_workspace_state.WorkspaceStateTests.test_invalid_saved_paths_and_identifiers_are_ignored"></a>

### `WorkspaceStateTests.test_invalid_saved_paths_and_identifiers_are_ignored`

```python
def test_invalid_saved_paths_and_identifiers_are_ignored(self)
```

<a id="symbol-tests.test_workspace_state.WorkspaceStateTests.test_navigation_snapshot_omits_file_lists_and_preserves_paths"></a>

### `WorkspaceStateTests.test_navigation_snapshot_omits_file_lists_and_preserves_paths`

```python
def test_navigation_snapshot_omits_file_lists_and_preserves_paths(self)
```

<a id="symbol-tests.test_workspace_state.WorkspaceStateTests.test_running_snapshot_does_not_invent_collapsed_folders_before_rows_exist"></a>

### `WorkspaceStateTests.test_running_snapshot_does_not_invent_collapsed_folders_before_rows_exist`

```python
def test_running_snapshot_does_not_invent_collapsed_folders_before_rows_exist(self)
```
