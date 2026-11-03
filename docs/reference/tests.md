# Справочник тестовых сценариев

Индекс существующих тестов, без изменения их реализации. Полный прогон: 380 тестов. Имена отражают проверяемые утверждения; файл и строка позволяют прочитать fixture, подмены и точные assert.

## `test_catalog.py`

Медиаиндекс, очередь и версии превью.

- [CatalogTests.test_scan_is_persistent_and_reconciles_removed_entries](../../tests/test_catalog.py#L12)
- [CatalogTests.test_folder_tree_contains_nested_directories](../../tests/test_catalog.py#L43)
- [CatalogTests.test_resolve_source_folder_stays_inside_source](../../tests/test_catalog.py#L63)
- [CatalogTests.test_resolve_media_file_returns_scanned_original](../../tests/test_catalog.py#L80)
- [CatalogTests.test_source_role_label_and_comment_can_be_updated](../../tests/test_catalog.py#L95)
- [CatalogTests.test_system_photos_source_is_virtual_and_groups_assets_by_month](../../tests/test_catalog.py#L120)
- [CatalogTests.test_thumbnail_queue_is_persistent_and_tracks_progress](../../tests/test_catalog.py#L145)

## `test_comparison.py`

Общая сверка имён и совместимость отчётов.

- [ComparisonTests.test_names_match_even_when_content_size_and_parent_location_differ](../../tests/test_comparison.py#L50)
- [ComparisonTests.test_same_content_with_different_name_is_not_a_name_match](../../tests/test_comparison.py#L61)
- [ComparisonTests.test_same_filename_in_other_folder_is_separate_status](../../tests/test_comparison.py#L66)
- [ComparisonTests.test_empty_directories_are_compared_and_file_directory_types_stay_distinct](../../tests/test_comparison.py#L75)
- [ComparisonTests.test_unicode_and_case_names_are_normalized](../../tests/test_comparison.py#L85)
- [ComparisonTests.test_never_reads_file_contents_or_requests_file_stat](../../tests/test_comparison.py#L91)
- [ComparisonTests.test_complete_lists_are_reused_offline_without_filesystem_access](../../tests/test_comparison.py#L118)
- [ComparisonTests.test_refresh_lists_is_explicit_and_reused_lists_keep_their_dates](../../tests/test_comparison.py#L132)
- [ComparisonTests.test_incomplete_target_prevents_absence_claim_but_keeps_matches](../../tests/test_comparison.py#L143)
- [ComparisonTests.test_unreadable_source_branch_is_visible_in_unverified_filter](../../tests/test_comparison.py#L158)
- [ComparisonTests.test_offline_source_without_a_complete_list_fails](../../tests/test_comparison.py#L172)
- [ComparisonTests.test_legacy_resume_creates_name_job_and_preserves_old_report_and_lists](../../tests/test_comparison.py#L178)
- [ComparisonTests.test_background_pause_resume_and_single_worker](../../tests/test_comparison.py#L197)
- [ComparisonTests.test_symlinks_special_files_and_originals_remain_untouched](../../tests/test_comparison.py#L222)
- [ComparisonTests.test_name_filter_keeps_ancestors_and_paginates](../../tests/test_comparison.py#L238)
- [ComparisonTests.test_two_target_locations_and_directory_matches_are_explained](../../tests/test_comparison.py#L248)
- [ComparisonTests.test_target_tree_expands_saved_subdirectories_without_accessing_nas](../../tests/test_comparison.py#L256)
- [ComparisonTests.test_target_tree_only_reads_target_scopes_in_the_requested_job](../../tests/test_comparison.py#L275)
- [ComparisonTests.test_same_named_matches_on_two_volumes_expand_independently](../../tests/test_comparison.py#L293)
- [ComparisonTests.test_target_tree_paginates_names_and_does_not_follow_symlinks](../../tests/test_comparison.py#L303)
- [ComparisonTests.test_directory_list_cache_is_available_in_explorer_offline](../../tests/test_comparison.py#L316)
- [ComparisonTests.test_scopes_do_not_reuse_another_directorys_list](../../tests/test_comparison.py#L324)
- [ComparisonTests.test_rejects_overlap_and_traversal_and_checks_mount_identity](../../tests/test_comparison.py#L332)
- [ComparisonTests.test_restart_leaves_interrupted_job_paused](../../tests/test_comparison.py#L340)
- [ComparisonTests.test_legacy_large_identifiers_still_roundtrip_without_loss](../../tests/test_comparison.py#L348)

## `test_comparison_tree_ui.py`

Дерево найденных путей и пагинация.

- [ComparisonTreeTests.test_opened_folder_keeps_matches_and_breadcrumb_navigation_within_its_scope](../../tests/test_comparison_tree_ui.py#L18)
- [ComparisonTreeTests.test_slow_folder_open_cannot_focus_previous_source_results](../../tests/test_comparison_tree_ui.py#L41)
- [ComparisonTreeTests.test_slow_folder_response_cannot_restore_results_from_previous_selection](../../tests/test_comparison_tree_ui.py#L60)
- [ComparisonTreeTests.test_identical_paths_on_two_targets_have_independent_folder_pages](../../tests/test_comparison_tree_ui.py#L84)

## `test_copies.py`

Наборы папок, нумерация и пересечения.

- [CopyCatalogTests.test_numbers_span_copy_types_and_labels_inherit_with_path_boundaries](../../tests/test_copies.py#L35)
- [CopyCatalogTests.test_registration_changes_no_files_and_does_not_require_fresh_directory_reads](../../tests/test_copies.py#L56)
- [CopyCatalogTests.test_idempotent_registration_does_not_allocate_extra_copy_numbers](../../tests/test_copies.py#L67)
- [CopyCatalogTests.test_rejects_files_unknown_paths_and_unverified_disks](../../tests/test_copies.py#L75)
- [CopyCatalogTests.test_overlapping_roots_cannot_give_descendants_conflicting_labels](../../tests/test_copies.py#L85)
- [CopyCatalogTests.test_offline_locations_and_changed_mount_names_preserve_relationships_after_restart](../../tests/test_copies.py#L98)
- [CopyCatalogTests.test_middle_deletion_requires_confirmed_renumbering_before_adding](../../tests/test_copies.py#L119)
- [CopyCatalogTests.test_last_deletion_reuses_number_and_ignores_legacy_counter](../../tests/test_copies.py#L149)
- [CopyCatalogTests.test_renumbering_compacts_multiple_gaps_atomically_without_changing_files](../../tests/test_copies.py#L167)
- [CopyCatalogTests.test_stale_renumbering_proposal_cannot_change_newer_links_or_types](../../tests/test_copies.py#L183)
- [CopyCatalogTests.test_concurrent_registrations_allocate_unique_consecutive_numbers](../../tests/test_copies.py#L201)
- [CopyCatalogTests.test_old_volume_roles_do_not_create_main_folders_or_links](../../tests/test_copies.py#L213)
- [CopyCatalogTests.test_folder_labels_and_tracking_are_independent_and_survive_restart_and_disconnect](../../tests/test_copies.py#L219)
- [CopyCatalogTests.test_old_catalog_gets_empty_settings_and_deleted_groups_leave_no_settings](../../tests/test_copies.py#L238)
- [CopyCatalogTests.test_invalid_settings_cannot_modify_a_group_or_create_orphan_records](../../tests/test_copies.py#L249)
- [CopyCatalogTests.test_only_tracked_groups_record_changes_and_stale_acknowledgements_preserve_new_changes](../../tests/test_copies.py#L260)

## `test_copy_connections.py`

Подключение и отключение связей.

- [CopyConnectionTests.test_disconnected_group_preserves_labels_numbers_and_history_after_restart](../../tests/test_copy_connections.py#L34)
- [CopyConnectionTests.test_individual_disconnect_survives_whole_group_round_trip_without_renumbering](../../tests/test_copy_connections.py#L59)
- [CopyConnectionTests.test_invalid_connections_and_explicit_deletion](../../tests/test_copy_connections.py#L75)
- [CopyConnectionTests.test_disconnect_removes_roles_from_tree_properties_and_saved_snapshots](../../tests/test_copy_connections.py#L109)
- [CopyConnectionTests.test_disconnected_copy_hides_only_its_own_role](../../tests/test_copy_connections.py#L121)
- [CopyConnectionTests.test_missing_disk_keeps_roles_when_relationship_was_not_disabled](../../tests/test_copy_connections.py#L131)
- [CopyConnectionTests.test_api_can_disconnect_and_reconnect_but_will_not_interrupt_copying](../../tests/test_copy_connections.py#L136)
- [SidebarSectionsTests.test_offline_copy_keeps_its_group_and_online_siblings_visible](../../tests/test_copy_connections.py#L170)
- [SidebarSectionsTests.test_offline_main_does_not_hide_online_copy_and_all_offline_moves_whole_group](../../tests/test_copy_connections.py#L179)
- [SidebarSectionsTests.test_manual_disconnect_remains_visible_while_unknown_availability_stays_active](../../tests/test_copy_connections.py#L188)
- [ConnectionActionsTests.test_disconnect_uses_reversible_api_unlinks_pair_and_opens_section](../../tests/test_copy_connections.py#L199)
- [ConnectionActionsTests.test_copying_blocks_disconnect_without_changing_any_state](../../tests/test_copy_connections.py#L213)

## `test_copy_files.py`

Планы, запись, гонки и незавершённые копии.

- [MissingCopyTests.test_preview_is_readonly_and_requires_a_completed_file_report](../../tests/test_copy_files.py#L62)
- [MissingCopyTests.test_only_missing_files_and_directories_are_created](../../tests/test_copy_files.py#L72)
- [MissingCopyTests.test_existing_target_created_after_preview_is_skipped](../../tests/test_copy_files.py#L98)
- [MissingCopyTests.test_target_appearing_at_publication_is_never_overwritten](../../tests/test_copy_files.py#L106)
- [MissingCopyTests.test_changed_source_since_report_is_not_copied](../../tests/test_copy_files.py#L121)
- [MissingCopyTests.test_preview_freezes_fresh_source_metadata_without_reading_file_contents](../../tests/test_copy_files.py#L129)
- [MissingCopyTests.test_source_replaced_by_fifo_does_not_block_or_copy](../../tests/test_copy_files.py#L140)
- [MissingCopyTests.test_source_changing_while_reading_leaves_no_final_or_partial_file](../../tests/test_copy_files.py#L149)
- [MissingCopyTests.test_stop_removes_only_the_incomplete_staging_file](../../tests/test_copy_files.py#L166)
- [MissingCopyTests.test_symlink_target_parent_is_not_followed](../../tests/test_copy_files.py#L184)
- [MissingCopyTests.test_target_root_replaced_after_preview_requires_new_preview](../../tests/test_copy_files.py#L194)
- [MissingCopyTests.test_parent_replaced_during_copy_is_detected_before_publication](../../tests/test_copy_files.py#L203)
- [MissingCopyTests.test_conflicting_parent_and_its_descendants_are_not_in_plan](../../tests/test_copy_files.py#L225)
- [MissingCopyTests.test_removed_link_and_offline_volume_cannot_start_a_plan](../../tests/test_copy_files.py#L237)
- [MissingCopyTests.test_no_space_fails_without_publishing_a_file](../../tests/test_copy_files.py#L247)
- [MissingCopyTests.test_completed_copy_creates_new_comparison_and_keeps_other_marks_and_old_report](../../tests/test_copy_files.py#L256)
- [MissingCopyTests.test_restart_records_interruption_and_next_explicit_copy_cleans_owned_staging](../../tests/test_copy_files.py#L276)
- [MissingCopyTests.test_registered_aliases_cannot_make_a_nested_copy_inside_the_source](../../tests/test_copy_files.py#L297)
- [MissingCopyTests.test_api_preview_and_execution_use_only_the_registered_direction](../../tests/test_copy_files.py#L309)
- [MissingCopyTests.test_running_copy_excludes_another_comparison_and_can_be_stopped](../../tests/test_copy_files.py#L340)
- [MissingCopyTests.test_network_copy_uses_exclusive_creation_without_atomic_rename](../../tests/test_copy_files.py#L365)
- [MissingCopyTests.test_unsupported_atomic_publication_falls_back_without_overwriting](../../tests/test_copy_files.py#L375)
- [MissingCopyTests.test_interrupted_network_copy_is_marked_even_when_its_size_already_matches](../../tests/test_copy_files.py#L384)
- [MissingCopyTests.test_network_target_appearing_before_exclusive_open_is_skipped](../../tests/test_copy_files.py#L412)

## `test_copy_number_release.py`

Освобождение номеров и история привязок.

- [CopyNumberReleaseTests.test_reuses_number_with_a_new_identity_and_preserves_old_record_after_restart](../../tests/test_copy_number_release.py#L46)
- [CopyNumberReleaseTests.test_other_copy_numbers_stay_unchanged_when_a_middle_number_is_released](../../tests/test_copy_number_release.py#L72)
- [CopyNumberReleaseTests.test_old_reports_and_completed_copy_journal_are_not_inherited_by_the_new_copy](../../tests/test_copy_number_release.py#L84)
- [CopyNumberReleaseTests.test_can_restore_only_when_both_number_and_folder_are_free](../../tests/test_copy_number_release.py#L112)
- [CopyNumberReleaseTests.test_released_folder_can_be_rebound_without_inheriting_the_old_identity](../../tests/test_copy_number_release.py#L124)
- [CopyNumberReleaseTests.test_restoration_rejects_a_folder_now_used_by_another_group](../../tests/test_copy_number_release.py#L131)
- [CopyNumberReleaseTests.test_active_main_and_stale_menu_snapshots_cannot_release_a_number](../../tests/test_copy_number_release.py#L139)
- [CopyNumberReleaseTests.test_release_is_idempotent_and_group_reconnection_does_not_restore_it](../../tests/test_copy_number_release.py#L149)
- [CopyNumberReleaseTests.test_concurrent_additions_reuse_the_released_number_once](../../tests/test_copy_number_release.py#L159)
- [CopyNumberReleaseTests.test_upgrade_preserves_existing_disconnections_without_releasing_any_number](../../tests/test_copy_number_release.py#L172)
- [CopyNumberReleaseTests.test_api_checks_expected_number_and_active_operations](../../tests/test_copy_number_release.py#L183)
- [ReleasedCopyUITests.test_archived_record_stays_in_disconnected_and_opens_history_without_live_folder_reads](../../tests/test_copy_number_release.py#L208)
- [ReleasedCopyUITests.test_history_view_rejects_queued_start_resume_and_copy_commands](../../tests/test_copy_number_release.py#L222)
- [ReleasedCopyUITests.test_history_view_does_not_offer_to_create_a_new_binding_from_old_report_paths](../../tests/test_copy_number_release.py#L234)

## `test_copy_sandbox.py`

Запрет записи существующих оригиналов в sandbox.

- [CopySandboxTests.test_folder_marker_write_exception_covers_only_its_service_filename](../../tests/test_copy_sandbox.py#L13)
- [CopySandboxTests.test_marker_rename_is_atomic_and_keeps_originals_protected](../../tests/test_copy_sandbox.py#L43)
- [CopySandboxTests.test_atomic_copy_keeps_existing_files_write_protected](../../tests/test_copy_sandbox.py#L73)
- [CopySandboxTests.test_network_direct_copy_keeps_existing_files_write_protected](../../tests/test_copy_sandbox.py#L76)

## `test_copy_sources.py`

Выбор источников и запрет циклов обычных копий.

- [CopySourceTests.test_second_copy_uses_first_in_comparison_and_actual_transfer](../../tests/test_copy_sources.py#L15)
- [CopySourceTests.test_cycles_cross_group_sources_and_self_sources_are_rejected](../../tests/test_copy_sources.py#L29)
- [CopySourceTests.test_disconnected_or_removed_source_never_falls_back_to_original](../../tests/test_copy_sources.py#L36)
- [CopySourceTests.test_change_invalidates_an_old_paused_comparison_and_plan](../../tests/test_copy_sources.py#L45)
- [CopySourceTests.test_old_copy_plan_is_rejected_after_changing_its_source](../../tests/test_copy_sources.py#L50)

## `test_directory_sizes.py`

Размеры, частичность, stale и UI-подписи.

- [DirectorySizeTests.test_recursive_totals_include_hidden_files_and_empty_folders_without_opening_contents](../../tests/test_directory_sizes.py#L42)
- [DirectorySizeTests.test_refresh_recomputes_and_cached_result_survives_restart_and_disconnect](../../tests/test_directory_sizes.py#L54)
- [DirectorySizeTests.test_changed_child_invalidates_ancestor_until_it_is_recalculated](../../tests/test_directory_sizes.py#L68)
- [DirectorySizeTests.test_reopening_old_cached_size_does_not_scan_again_or_discover_disks](../../tests/test_directory_sizes.py#L78)
- [DirectorySizeTests.test_parent_request_covers_child_without_blocking_or_duplicate_traversals](../../tests/test_directory_sizes.py#L88)
- [DirectorySizeTests.test_partial_scan_is_not_reported_as_a_complete_folder](../../tests/test_directory_sizes.py#L107)
- [DirectorySizeTests.test_failed_refresh_preserves_previous_size](../../tests/test_directory_sizes.py#L122)
- [DirectorySizeTests.test_paths_links_and_replaced_volumes_are_rejected](../../tests/test_directory_sizes.py#L130)
- [DirectorySizeDisplayTests.test_zero_partial_refresh_and_offline_values_are_distinct](../../tests/test_directory_sizes.py#L152)
- [DirectorySizeDisplayTests.test_header_follows_folder_navigation_and_file_parent_and_hides_missing_side](../../tests/test_directory_sizes.py#L164)
- [DirectorySizeDisplayTests.test_deleted_rows_are_not_updated_while_a_folder_is_loading](../../tests/test_directory_sizes.py#L181)
- [FolderLoadingTests.test_folder_list_does_not_wait_for_a_blocked_size_request](../../tests/test_directory_sizes.py#L193)
- [FolderLoadingTests.test_cached_tree_is_rendered_before_slow_live_directory_read](../../tests/test_directory_sizes.py#L209)
- [RefreshButtonTests.test_rapid_clicks_and_second_pane_do_not_repeat_refresh_until_calculation_finishes](../../tests/test_directory_sizes.py#L282)
- [RefreshButtonTests.test_completed_failed_and_offline_calculations_release_the_button](../../tests/test_directory_sizes.py#L325)
- [RefreshButtonTests.test_navigation_during_refresh_does_not_clear_the_new_folder](../../tests/test_directory_sizes.py#L333)
- [RefreshButtonTests.test_forced_refresh_does_not_recalculate_other_visible_folders](../../tests/test_directory_sizes.py#L348)
- [RefreshButtonTests.test_failed_size_request_releases_the_button_without_queuing_another_request](../../tests/test_directory_sizes.py#L365)

## `test_folder_markers.py`

Принадлежность, публикация и повтор маркеров папок.

- [FolderMarkerTests.test_all_registered_roots_get_own_ids_and_readable_roles_without_changing_data](../../tests/test_folder_markers.py#L54)
- [FolderMarkerTests.test_rechecking_unchanged_markers_does_not_rewrite_the_files](../../tests/test_folder_markers.py#L68)
- [FolderMarkerTests.test_connection_kind_and_release_changes_reach_the_same_folder_marker](../../tests/test_folder_markers.py#L76)
- [FolderMarkerTests.test_offline_or_missing_folder_is_retried_without_creating_directories](../../tests/test_folder_markers.py#L92)
- [FolderMarkerTests.test_foreign_marker_symlink_fifo_and_oversized_file_are_preserved](../../tests/test_folder_markers.py#L109)
- [FolderMarkerTests.test_failed_atomic_update_preserves_the_previous_document_and_cleans_temporary_files](../../tests/test_folder_markers.py#L132)
- [FolderMarkerTests.test_metadata_change_during_a_write_keeps_the_newer_revision_pending](../../tests/test_folder_markers.py#L144)
- [FolderMarkerTests.test_a_marker_appearing_during_creation_is_not_overwritten](../../tests/test_folder_markers.py#L161)
- [FolderMarkerTests.test_smb_exclusive_creation_fallback_still_never_overwrites_existing_files](../../tests/test_folder_markers.py#L171)
- [FolderMarkerTests.test_reusing_a_released_path_writes_the_new_identity_without_old_job_overwriting_it](../../tests/test_folder_markers.py#L177)
- [FolderMarkerTests.test_existing_catalog_backfill_and_pending_changes_survive_restart](../../tests/test_folder_markers.py#L189)
- [FolderMarkerTests.test_only_the_latest_binding_can_describe_a_path_with_several_old_generations](../../tests/test_folder_markers.py#L200)
- [FolderMarkerTests.test_deleted_bindings_are_marked_removed_without_deleting_source_files](../../tests/test_folder_markers.py#L213)
- [FolderMarkerTests.test_unverified_volume_never_receives_folder_writes](../../tests/test_folder_markers.py#L221)
- [FolderMarkerTests.test_service_files_are_excluded_from_lists_sizes_both_comparisons_and_data_copying](../../tests/test_folder_markers.py#L230)

## `test_folder_tags.py`

Пользовательские метки папок.

- [FolderTagTests.test_multiple_tags_persist_without_changing_annotations_or_original_files](../../tests/test_folder_tags.py#L26)
- [FolderTagTests.test_tags_apply_only_to_the_selected_folder_and_update_cached_listings](../../tests/test_folder_tags.py#L37)
- [FolderTagTests.test_system_and_unknown_tags_are_rejected_without_changing_existing_tags](../../tests/test_folder_tags.py#L49)
- [FolderTagTests.test_files_symlinks_unknown_paths_and_traversal_cannot_receive_folder_tags](../../tests/test_folder_tags.py#L56)
- [FolderTagTests.test_old_database_gains_tag_table_without_losing_existing_metadata](../../tests/test_folder_tags.py#L66)
- [FolderTagTests.test_tags_do_not_transfer_to_another_disk_at_the_same_mount_point](../../tests/test_folder_tags.py#L74)
- [FolderTagTests.test_api_supports_multiple_tags_and_forbids_the_automatic_library_tag](../../tests/test_folder_tags.py#L81)
- [FolderTagTests.test_saved_tag_changes_update_both_open_trees_without_reloading_directories](../../tests/test_folder_tags.py#L100)

## `test_folder_tracking.py`

Watchdog и подтверждение изменений.

- [FolderTrackingTests.test_only_opted_in_folders_subscribe_and_events_persist_after_restart](../../tests/test_folder_tracking.py#L46)
- [FolderTrackingTests.test_read_events_and_copy_temporaries_do_not_trigger_a_change](../../tests/test_folder_tracking.py#L57)
- [FolderTrackingTests.test_offline_and_disabled_folders_detach_and_stale_events_are_ignored](../../tests/test_folder_tracking.py#L69)
- [FolderTrackingTests.test_manual_group_disconnect_stops_tracking_until_reconnected](../../tests/test_folder_tracking.py#L82)
- [FolderTrackingTests.test_reconnect_restores_tracking_and_replaced_or_symlink_roots_are_rejected](../../tests/test_folder_tracking.py#L93)
- [FolderTrackingTests.test_actual_observer_detects_nested_file_changes](../../tests/test_folder_tracking.py#L114)
- [FolderTrackingTests.test_api_settings_validation_and_partial_updates](../../tests/test_folder_tracking.py#L131)

## `test_network.py`

Bonjour, ресурсы SMB и ошибки.

- [NetworkParsingTests.test_bonjour_keeps_other_interface_after_remove](../../tests/test_network.py#L30)
- [NetworkParsingTests.test_discovery_merges_two_advertisements_of_same_server](../../tests/test_network.py#L34)
- [NetworkParsingTests.test_lists_disk_shares_only_and_keeps_spaces_unicode](../../tests/test_network.py#L43)
- [NetworkParsingTests.test_no_password_prompt_or_mount_in_share_enumeration](../../tests/test_network.py#L51)
- [NetworkParsingTests.test_diagnostics_do_not_expose_account_or_password](../../tests/test_network.py#L59)
- [NetworkCatalogTests.test_remember_unmounted_resource_and_roles_without_os_actions](../../tests/test_network.py#L81)
- [NetworkCatalogTests.test_existing_volume_keeps_identity_role_and_snapshot](../../tests/test_network.py#L95)
- [NetworkCatalogTests.test_resource_matches_mount_by_other_bonjour_alias_without_duplicate](../../tests/test_network.py#L107)
- [NetworkCatalogTests.test_auth_error_preserves_share_list](../../tests/test_network.py#L117)
- [NetworkCatalogTests.test_offline_server_and_missing_resource_remain_remembered](../../tests/test_network.py#L125)
- [NetworkCatalogTests.test_failed_scan_preserves_previous_discovery](../../tests/test_network.py#L137)
- [NetworkCatalogTests.test_unknown_share_is_rejected_and_finder_requires_explicit_command](../../tests/test_network.py#L143)
- [NetworkCatalogTests.test_nas_and_m4_groups_survive_disconnection_and_restart](../../tests/test_network.py#L151)
- [NetworkCatalogTests.test_same_share_names_on_different_servers_stay_in_separate_groups](../../tests/test_network.py#L169)
- [NetworkCatalogTests.test_legacy_offline_group_is_matched_by_identity_not_share_name](../../tests/test_network.py#L178)
- [NetworkCatalogTests.test_legacy_volume_table_is_not_altered](../../tests/test_network.py#L187)

## `test_paired_comparison.py`

Выровненная структура, размеры и SHA-256.

- [PairedComparisonTests.test_folder_comparison_uses_relative_paths_and_reports_both_directions](../../tests/test_paired_comparison.py#L46)
- [PairedComparisonTests.test_folder_stage_never_opens_file_contents](../../tests/test_paired_comparison.py#L61)
- [PairedComparisonTests.test_full_stage_checks_content_and_keeps_files_original](../../tests/test_paired_comparison.py#L74)
- [PairedComparisonTests.test_default_file_check_compares_names_and_sizes_without_reading_contents](../../tests/test_paired_comparison.py#L93)
- [PairedComparisonTests.test_difference_pages_keep_root_folders_alongside_differences_and_their_parents](../../tests/test_paired_comparison.py#L122)
- [PairedComparisonTests.test_matching_reports_keep_root_folders_without_matching_files_for_both_methods](../../tests/test_paired_comparison.py#L137)
- [PairedComparisonTests.test_upgrade_preserves_old_reports_as_sha256](../../tests/test_paired_comparison.py#L150)
- [PairedComparisonTests.test_full_stage_requires_finished_folder_check_for_same_pair](../../tests/test_paired_comparison.py#L161)
- [PairedComparisonTests.test_failed_directory_does_not_turn_unknown_data_into_absence](../../tests/test_paired_comparison.py#L168)
- [PairedComparisonTests.test_symlinks_and_special_files_are_not_followed_and_type_conflicts_are_visible](../../tests/test_paired_comparison.py#L184)
- [PairedComparisonTests.test_extra_copy_decisions_are_records_and_do_not_change_disks](../../tests/test_paired_comparison.py#L197)
- [PairedComparisonTests.test_file_changed_while_hashing_is_unverified](../../tests/test_paired_comparison.py#L211)
- [PairedComparisonTests.test_folder_decisions_inherit_and_survive_the_file_stage](../../tests/test_paired_comparison.py#L230)
- [PairedComparisonTests.test_offline_side_is_unknown_and_interrupted_jobs_can_be_resumed](../../tests/test_paired_comparison.py#L246)
- [PairedComparisonTests.test_pause_resume_restart_and_saved_results](../../tests/test_paired_comparison.py#L260)

## `test_paired_workspace.py`

Связанные панели, просмотр и история.

- [PairedWorkspaceTests.test_expanding_one_folder_reveals_only_its_differing_files](../../tests/test_paired_workspace.py#L31)
- [PairedWorkspaceTests.test_fully_matching_report_keeps_root_folders_collapsed](../../tests/test_paired_workspace.py#L40)
- [PairedWorkspaceTests.test_root_files_require_explicit_disclosure_even_after_navigation](../../tests/test_paired_workspace.py#L49)
- [ReportExpansionTests.test_only_branches_with_differences_expand_and_manual_changes_survive_reload](../../tests/test_paired_workspace.py#L72)
- [ReportExpansionTests.test_file_stage_still_leaves_every_folder_closed_until_manual_expansion](../../tests/test_paired_workspace.py#L83)
- [PairedContextMenuTests.test_finder_uses_the_clicked_side_and_its_full_volume_path](../../tests/test_paired_workspace.py#L101)
- [PairedContextMenuTests.test_properties_and_decisions_remain_separate_menu_actions](../../tests/test_paired_workspace.py#L110)
- [PairedContextMenuTests.test_missing_side_does_not_open_another_sides_file](../../tests/test_paired_workspace.py#L118)
- [PairedContextMenuTests.test_open_menu_blocks_background_refresh_until_closed](../../tests/test_paired_workspace.py#L123)
- [BreadcrumbNavigationTests.test_delayed_selector_event_cannot_reset_the_clicked_parent](../../tests/test_paired_workspace.py#L132)
- [BreadcrumbNavigationTests.test_parent_and_volume_root_leave_the_pair_on_the_clicked_side](../../tests/test_paired_workspace.py#L144)
- [BreadcrumbNavigationTests.test_source_report_parent_opens_normal_browsing](../../tests/test_paired_workspace.py#L159)
- [BreadcrumbNavigationTests.test_opening_parent_uses_existing_unlink_without_removing_records](../../tests/test_paired_workspace.py#L168)
- [ComparisonToolbarTests.test_all_three_actions_ignore_queued_clicks_in_any_comparison_state](../../tests/test_paired_workspace.py#L179)
- [ComparisonToolbarTests.test_linked_browsing_without_a_report_keeps_navigation_available](../../tests/test_paired_workspace.py#L200)
- [PanelUnlinkTests.test_panel_unlink_restores_browsing_without_removing_copy_records](../../tests/test_paired_workspace.py#L228)
- [PanelUnlinkTests.test_leaving_a_running_comparison_stops_it_before_restoring_the_panels](../../tests/test_paired_workspace.py#L238)
- [MainFolderOpeningTests.test_main_opens_the_first_numbered_copy_in_linked_panels](../../tests/test_paired_workspace.py#L253)
- [MainFolderOpeningTests.test_main_without_copies_opens_only_the_main_folder](../../tests/test_paired_workspace.py#L261)
- [CopyRemovalConfirmationTests.test_cancel_shows_both_locations_without_deleting_the_link](../../tests/test_paired_workspace.py#L282)
- [CopyRemovalConfirmationTests.test_confirm_removes_only_the_chosen_link_then_closes_its_pair](../../tests/test_paired_workspace.py#L290)

## `test_photo_copy_roles.py`

Метки привязанных копий Photos.

- [PhotoCopyRoleTests.test_bound_copy_has_its_own_number_and_library_tag_while_photos_is_offline](../../tests/test_photo_copy_roles.py#L20)
- [PhotoCopyRoleTests.test_only_the_exact_bound_folder_gets_the_library_role](../../tests/test_photo_copy_roles.py#L29)
- [PhotoCopyRoleTests.test_disconnecting_library_copy_removes_its_tags_and_preserves_other_roles](../../tests/test_photo_copy_roles.py#L35)
- [PhotoCopyRoleTests.test_refresh_updates_tags_after_rebinding_but_not_on_progress_changes](../../tests/test_photo_copy_roles.py#L45)

## `test_photo_libraries.py`

Идентичность и профили медиатек.

- [PhotoLibrariesTests.test_migration_preserves_media_ids_and_existing_cached_previews_without_access](../../tests/test_photo_libraries.py#L67)
- [PhotoLibrariesTests.test_switching_accounts_keeps_old_catalogue_and_copy_associations](../../tests/test_photo_libraries.py#L78)
- [PhotoLibrariesTests.test_thumbnail_identity_guard_stops_a_changed_library_before_writing](../../tests/test_photo_libraries.py#L96)
- [PhotoLibrariesTests.test_small_photokit_preview_stays_visible_while_waiting_for_a_larger_local_image](../../tests/test_photo_libraries.py#L105)
- [PhotoLibrariesTests.test_resuming_photos_does_not_resume_the_paused_folder_queue_and_includes_video](../../tests/test_photo_libraries.py#L127)
- [PhotoLibrariesTests.test_cloud_waits_do_not_block_the_next_asset_or_count_as_errors](../../tests/test_photo_libraries.py#L141)
- [PhotoLibrariesTests.test_copy_binding_and_unbinding_never_write_originals_or_touch_destination_files](../../tests/test_photo_libraries.py#L153)
- [PhotoLibrariesTests.test_copy_targets_reject_symlinks_parent_traversal_and_overlapping_libraries](../../tests/test_photo_libraries.py#L164)
- [PhotoLibrariesTests.test_renaming_survives_legacy_source_registration_and_restart](../../tests/test_photo_libraries.py#L177)
- [PhotoLibrariesTests.test_photokit_scan_without_resource_sizes_preserves_known_original_sizes](../../tests/test_photo_libraries.py#L183)
- [PhotoLibrariesTests.test_copy_receipts_are_metadata_only_and_survive_removed_photos](../../tests/test_photo_libraries.py#L189)
- [PhotoLibrariesTests.test_sidebar_progress_and_cloud_wait_states_are_separate](../../tests/test_photo_libraries.py#L201)

## `test_photos_adapter.py`

NDJSON, Unix-сокет, отмена и границы блоков.

- [PhotosAdapterTests.test_preview_requests_reuse_one_process_and_do_not_export_an_original](../../tests/test_photos_adapter.py#L44)
- [PhotosAdapterTests.test_missing_photokit_permission_never_falls_back_to_full_image_export](../../tests/test_photos_adapter.py#L54)
- [PhotosAdapterTests.test_gui_socket_transport_reuses_the_launched_app_and_keeps_socket_private](../../tests/test_photos_adapter.py#L62)
- [PhotosAdapterTests.test_gui_refuses_an_insecure_or_symlinked_ipc_directory](../../tests/test_photos_adapter.py#L88)
- [PhotosAdapterTests.test_transport_statuses_distinguish_account_change_permission_and_cloud_wait](../../tests/test_photos_adapter.py#L105)
- [PhotosAdapterTests.test_original_stream_decodes_bounded_chunks_and_verifies_protocol_trailer](../../tests/test_photos_adapter.py#L113)
- [PhotosAdapterTests.test_stream_cancellation_sends_matching_token_and_stops_consumer](../../tests/test_photos_adapter.py#L129)
- [PhotosAdapterTests.test_consumer_error_closes_only_its_transport_and_rejects_oversized_chunks](../../tests/test_photos_adapter.py#L140)

## `test_photos_browser.py`

Годы/месяцы, страницы и виртуальные ID.

- [PhotosBrowserTests.test_offline_catalogue_opens_as_year_month_and_file_without_calling_photos](../../tests/test_photos_browser.py#L26)
- [PhotosBrowserTests.test_pagination_includes_every_object_even_with_duplicate_filenames](../../tests/test_photos_browser.py#L39)
- [PhotosBrowserTests.test_paths_and_preview_status_are_scoped_to_the_chosen_library](../../tests/test_photos_browser.py#L54)
- [PhotosBrowserTests.test_empty_and_undated_catalogues_remain_browsable](../../tests/test_photos_browser.py#L67)

## `test_photos_copy_chain.py`

Источники Photos, квитанции и цепочки копий.

- [PhotosCopyChainTests.test_existing_hdd_originals_seed_nvme_without_photos_download_or_hdd_rewrite](../../tests/test_photos_copy_chain.py#L29)
- [PhotosCopyChainTests.test_new_original_downloaded_once_then_copied_to_hdd_and_restart_preserves_progress](../../tests/test_photos_copy_chain.py#L40)
- [PhotosCopyChainTests.test_missing_known_hdd_file_waits_instead_of_redownloading_it](../../tests/test_photos_copy_chain.py#L59)
- [PhotosCopyChainTests.test_cycle_is_rejected_and_receipts_keep_their_ids_when_renumbered](../../tests/test_photos_copy_chain.py#L65)
- [PhotosCopyChainTests.test_pause_during_hdd_to_nvme_transfer_recovers_without_network](../../tests/test_photos_copy_chain.py#L71)
- [PhotosCopyChainTests.test_replication_happens_before_all_photos_downloads_finish](../../tests/test_photos_copy_chain.py#L94)
- [PhotosCopyChainTests.test_offline_second_copy_does_not_redirect_downloads_or_block_first_copy](../../tests/test_photos_copy_chain.py#L107)
- [PhotosCopyChainTests.test_source_metadata_change_blocks_seed_without_photos_fallback](../../tests/test_photos_copy_chain.py#L123)
- [PhotosCopyChainTests.test_pause_during_replica_inventory_leaves_no_stuck_running_job](../../tests/test_photos_copy_chain.py#L130)

## `test_photos_originals.py`

Прямая запись, версии, продолжение и частичные ресурсы.

- [PhotosOriginalsTests.test_streams_all_live_photo_resources_and_keeps_only_metadata_in_database](../../tests/test_photos_originals.py#L75)
- [PhotosOriginalsTests.test_adopts_manual_copy_by_name_size_and_metadata_and_preserves_name_collision](../../tests/test_photos_originals.py#L91)
- [PhotosOriginalsTests.test_first_and_second_runs_never_read_media_for_verification](../../tests/test_photos_originals.py#L105)
- [PhotosOriginalsTests.test_changed_existing_original_is_preserved_and_downloaded_to_a_free_name](../../tests/test_photos_originals.py#L114)
- [PhotosOriginalsTests.test_stream_size_mismatch_never_creates_receipts_or_completed_assets](../../tests/test_photos_originals.py#L124)
- [PhotosOriginalsTests.test_pause_mid_stream_and_resume_preserve_finished_resources](../../tests/test_photos_originals.py#L133)
- [PhotosOriginalsTests.test_unbinding_or_account_change_stops_before_any_final_file](../../tests/test_photos_originals.py#L149)
- [PhotosOriginalsTests.test_symlinked_destination_cannot_escape_the_bound_copy](../../tests/test_photos_originals.py#L168)
- [PhotosOriginalsTests.test_copy_writes_once_without_rename_readback_or_temporary_media](../../tests/test_photos_originals.py#L176)
- [PhotosOriginalsTests.test_disk_full_does_not_publish_or_count_an_original](../../tests/test_photos_originals.py#L193)
- [PhotosOriginalsTests.test_restart_turns_active_job_into_resumable_pause](../../tests/test_photos_originals.py#L203)
- [PhotosOriginalsTests.test_replaced_root_is_rejected_on_resume](../../tests/test_photos_originals.py#L211)
- [PhotosOriginalsTests.test_interrupted_smb_final_is_preserved_and_reported_on_retry](../../tests/test_photos_originals.py#L219)
- [PhotosOriginalsTests.test_file_appearing_before_exclusive_creation_is_never_replaced](../../tests/test_photos_originals.py#L240)
- [PhotosOriginalsTests.test_changed_written_size_never_creates_a_receipt](../../tests/test_photos_originals.py#L256)
- [PhotosOriginalsTests.test_chunks_are_combined_into_bounded_blocks_and_tail_is_flushed_once](../../tests/test_photos_originals.py#L268)
- [PhotosOriginalsTests.test_pause_before_buffer_flush_creates_no_incomplete_file](../../tests/test_photos_originals.py#L287)
- [PhotosOriginalsTests.test_pause_after_one_block_preserves_partial_file_and_resume_uses_free_name](../../tests/test_photos_originals.py#L297)
- [PhotosOriginalsTests.test_short_os_writes_still_save_every_byte](../../tests/test_photos_originals.py#L314)
- [PhotosOriginalsTests.test_fsync_failure_is_journalled_even_when_size_matches](../../tests/test_photos_originals.py#L321)
- [PhotosOriginalsTests.test_resume_keeps_progress_during_inventory_and_partial_manifest](../../tests/test_photos_originals.py#L331)
- [PhotosOriginalsTests.test_legacy_reset_manifest_recovers_all_receipts_before_resume](../../tests/test_photos_originals.py#L353)
- [PhotosOriginalsTests.test_changed_mtime_even_at_same_size_is_saved_to_a_free_name](../../tests/test_photos_originals.py#L365)
- [PhotosOriginalsTests.test_missing_receipt_file_is_downloaded_again_without_rereading_other_files](../../tests/test_photos_originals.py#L376)
- [PhotosOriginalsTests.test_changed_photos_version_does_not_reuse_an_old_receipt_or_overwrite_it](../../tests/test_photos_originals.py#L385)
- [PhotosOriginalsTests.test_metadata_preserving_changes_are_not_read_or_content_compared](../../tests/test_photos_originals.py#L395)
- [PhotosOriginalsTests.test_ambiguous_manual_names_are_not_adopted](../../tests/test_photos_originals.py#L406)
- [PhotosOriginalsTests.test_manual_file_changed_after_inventory_is_not_adopted](../../tests/test_photos_originals.py#L416)
- [PhotosOriginalsTests.test_unknown_staging_file_is_never_deleted](../../tests/test_photos_originals.py#L429)
- [PhotosOriginalsTests.test_original_worker_closes_every_database_connection](../../tests/test_photos_originals.py#L437)

## `test_photos_schedule.py`

Окна времени, повторные запросы и ручная пауза.

- [PhotosWindowTests.test_moscow_window_uses_local_time_and_exact_boundaries](../../tests/test_photos_schedule.py#L16)
- [PhotosWindowTests.test_window_crossing_midnight_has_one_daily_identity](../../tests/test_photos_schedule.py#L27)
- [PhotosScheduleTests.test_daytime_request_is_queued_without_opening_or_scanning_the_copy](../../tests/test_photos_schedule.py#L58)
- [PhotosScheduleTests.test_thumbnail_claims_scan_and_new_thumbnail_generation_wait_for_night](../../tests/test_photos_schedule.py#L68)
- [PhotosScheduleTests.test_scheduler_starts_at_midnight_and_does_not_repeat_a_finished_run](../../tests/test_photos_schedule.py#L81)
- [PhotosScheduleTests.test_window_end_cancels_current_resource_and_resumes_the_next_night](../../tests/test_photos_schedule.py#L102)
- [PhotosScheduleTests.test_manual_pause_cancels_automatic_resume_even_after_changing_hours](../../tests/test_photos_schedule.py#L122)
- [PhotosScheduleTests.test_manual_preview_pause_survives_the_night_window](../../tests/test_photos_schedule.py#L135)
- [PhotosScheduleTests.test_settings_and_queued_requests_survive_a_core_restart](../../tests/test_photos_schedule.py#L145)
- [PhotosScheduleTests.test_interrupted_night_run_resumes_after_restart_within_the_same_window](../../tests/test_photos_schedule.py#L159)
- [PhotosScheduleTests.test_daytime_enable_defers_started_work_and_disabling_allows_continuation](../../tests/test_photos_schedule.py#L176)
- [PhotosScheduleTests.test_unbound_copy_or_another_account_cannot_start_from_the_timer](../../tests/test_photos_schedule.py#L188)
- [PhotosScheduleTests.test_invalid_windows_are_rejected_without_changing_the_policy](../../tests/test_photos_schedule.py#L201)
- [PhotosScheduleTests.test_inactive_window_does_not_pause_ordinary_folder_previews](../../tests/test_photos_schedule.py#L207)
- [PhotosScheduleTests.test_source_card_distinguishes_manual_pause_and_waiting_for_night](../../tests/test_photos_schedule.py#L213)
- [PhotosScheduleTests.test_schedule_api_persists_window_and_original_start_respects_it](../../tests/test_photos_schedule.py#L220)

## `test_refresh_renamed_folder.py`

Обновление переименованной области UI.

- [RefreshRenamedFolderTests.test_refresh_shows_new_names_and_leaves_the_missing_selection_at_its_parent](../../tests/test_refresh_renamed_folder.py#L46)
- [RefreshRenamedFolderTests.test_a_renamed_browser_root_falls_back_to_a_readable_parent](../../tests/test_refresh_renamed_folder.py#L59)
- [RefreshRenamedFolderTests.test_renamed_nested_parent_falls_back_to_nearest_existing_ancestor](../../tests/test_refresh_renamed_folder.py#L67)
- [RefreshRenamedFolderTests.test_refresh_of_an_existing_folder_also_updates_its_parent_listing](../../tests/test_refresh_renamed_folder.py#L75)
- [RefreshRenamedFolderTests.test_permissions_failure_keeps_cached_entries_and_does_not_claim_the_folder_disappeared](../../tests/test_refresh_renamed_folder.py#L85)
- [RefreshRenamedFolderTests.test_a_renamed_file_clears_old_selection_and_updates_the_list](../../tests/test_refresh_renamed_folder.py#L94)

## `test_scanner.py`

Рекурсивный обход и ошибки обычного источника.

- [ScannerTests.test_scans_nested_media_and_ignores_other_files](../../tests/test_scanner.py#L12)
- [ScannerTests.test_does_not_follow_symbolic_links](../../tests/test_scanner.py#L31)
- [ScannerTests.test_ignores_macos_metadata_files_and_directories](../../tests/test_scanner.py#L44)

## `test_service_runtime.py`

Ротация журналов и отказ потока.

- [ServiceRuntimeTests.test_large_stdout_and_stderr_do_not_block_the_launcher_pipe](../../tests/test_service_runtime.py#L29)
- [ServiceRuntimeTests.test_module_arguments_still_work](../../tests/test_service_runtime.py#L37)
- [ServiceRuntimeTests.test_logs_rotate_and_keep_utf8_text](../../tests/test_service_runtime.py#L42)
- [ServiceRuntimeTests.test_failed_log_write_does_not_recurse_into_stderr](../../tests/test_service_runtime.py#L56)

## `test_sidebar_state.py`

Сохранение раскрытия боковых секций.

- [SidebarStateTests.test_browser_state_survives_new_page_and_storage_reload](../../tests/test_sidebar_state.py#L26)
- [SidebarStateTests.test_first_page_has_stable_defaults_without_creating_preferences](../../tests/test_sidebar_state.py#L44)
- [SidebarStateTests.test_another_tab_changing_one_section_preserves_the_others](../../tests/test_sidebar_state.py#L51)
- [SidebarStateTests.test_invalid_preferences_do_not_expand_or_hide_unrelated_sections](../../tests/test_sidebar_state.py#L62)
- [SidebarRefreshTests.test_loading_or_polling_copy_groups_never_toggles_volumes](../../tests/test_sidebar_state.py#L70)

## `test_storage.py`

Снимки, отключение и метаданные томов.

- [StorageTests.test_lists_all_types_and_empty_directories_without_writing_originals](../../tests/test_storage.py#L27)
- [StorageTests.test_disconnected_tree_and_roles_survive_restart](../../tests/test_storage.py#L39)
- [StorageTests.test_new_disk_at_same_mount_path_does_not_inherit_roles_or_snapshots](../../tests/test_storage.py#L54)
- [StorageTests.test_directory_refresh_rechecks_identity_even_within_discovery_cache](../../tests/test_storage.py#L65)
- [StorageTests.test_mount_replaced_between_discovery_and_open_preserves_snapshot](../../tests/test_storage.py#L72)
- [StorageTests.test_roles_inherit_and_can_be_cleared_or_overridden](../../tests/test_storage.py#L79)
- [StorageTests.test_rejects_traversal_symlinks_and_roles_for_arbitrary_paths](../../tests/test_storage.py#L95)
- [StorageTests.test_read_failure_preserves_last_successful_snapshot](../../tests/test_storage.py#L108)
- [StorageTests.test_cached_directory_does_not_wait_for_mount_discovery](../../tests/test_storage.py#L117)
- [StorageTests.test_finder_opens_volumes_and_folders_and_reveals_files_and_links](../../tests/test_storage.py#L142)
- [StorageTests.test_finder_rejects_missing_entries_traversal_and_symlink_parents](../../tests/test_storage.py#L154)
- [StorageTests.test_finder_rechecks_volume_identity_and_availability_before_opening](../../tests/test_storage.py#L162)
- [StorageTests.test_finder_reports_launch_failure_and_timeout](../../tests/test_storage.py#L176)
- [StorageTests.test_discovery_failure_is_unknown_not_offline](../../tests/test_storage.py#L182)
- [StorageTests.test_removed_share_archives_without_breaking_other_volumes_and_can_return](../../tests/test_storage.py#L188)
- [StorageTests.test_network_identity_ignores_username_and_mount_point](../../tests/test_storage.py#L243)

## `test_storage_previews.py`

Производные JPEG, видео и режим превью.

- [StoragePreviewTests.test_derivatives_have_two_sizes_reuse_cache_and_leave_original_unchanged](../../tests/test_storage_previews.py#L36)
- [StoragePreviewTests.test_replacement_invalidates_cache_and_tiles_do_not_discover_all_disks](../../tests/test_storage_previews.py#L52)
- [StoragePreviewTests.test_absolute_paths_parent_traversal_symlinks_and_fifos_are_refused](../../tests/test_storage_previews.py#L62)
- [StoragePreviewTests.test_offline_or_replaced_disk_is_not_read_even_when_a_derivative_exists](../../tests/test_storage_previews.py#L74)
- [StoragePreviewTests.test_video_frame_from_checked_descriptor_and_macos_fallback](../../tests/test_storage_previews.py#L82)
- [PreviewNavigationTests.test_slow_folder_response_cannot_replace_a_newer_file_selection](../../tests/test_storage_previews.py#L111)
- [PreviewNavigationTests.test_only_opposite_preview_receives_selection_and_keeps_its_tree_state](../../tests/test_storage_previews.py#L129)
- [PreviewNavigationTests.test_modes_restore_without_changing_saved_tree_position](../../tests/test_storage_previews.py#L142)
- [PreviewNavigationTests.test_preview_path_is_saved_separately_and_validated](../../tests/test_storage_previews.py#L158)

## `test_thumbnails.py`

Версии кэша, ориентация и генерация фото.

- [ThumbnailTests.test_missing_external_cache_does_not_fall_back_to_system_disk](../../tests/test_thumbnails.py#L21)
- [ThumbnailTests.test_thumbnail_is_written_only_to_cache](../../tests/test_thumbnails.py#L39)
- [ThumbnailTests.test_reused_media_id_does_not_reuse_another_files_thumbnail](../../tests/test_thumbnails.py#L68)

## `test_tree_keyboard.py`

Выделение, фокус и клавиатурная навигация.

- [TreeKeyboardTests.test_arrow_selection_does_not_toggle_or_rebuild_a_folder](../../tests/test_tree_keyboard.py#L30)
- [TreeKeyboardTests.test_stale_events_and_dialog_or_preview_focus_do_not_move_the_tree](../../tests/test_tree_keyboard.py#L35)
- [TreeKeyboardTests.test_comparison_arrow_selection_preserves_collapsed_folders](../../tests/test_tree_keyboard.py#L46)
- [TreeKeyboardTests.test_paired_arrow_keeps_a_collapsed_folder_closed_and_updates_both_sides](../../tests/test_tree_keyboard.py#L61)
- [TreeKeyboardTests.test_disconnected_sources_are_hidden_but_the_current_caption_is_preserved](../../tests/test_tree_keyboard.py#L76)
- [TreeKeyboardJavaScriptTests.test_rendered_rows_boundaries_inputs_and_new_render_revision](../../tests/test_tree_keyboard.py#L108)
- [TreeKeyboardJavaScriptTests.test_virtual_tree_moves_beyond_the_viewport_and_ignores_old_server_selection](../../tests/test_tree_keyboard.py#L135)

## `test_ui_connection.py`

Повторное использование HTTP-пула.

- [UIConnectionTests.test_core_polling_reuses_a_connection_pool_and_closes_it_on_shutdown](../../tests/test_ui_connection.py#L8)

## `test_volume_identity.py`

Маркеры, смена носителя и ёмкость.

- [VolumeIdentityTests.test_registration_writes_only_marker_and_survives_share_alias_restart](../../tests/test_volume_identity.py#L50)
- [VolumeIdentityTests.test_other_disk_at_same_share_cannot_inherit_history](../../tests/test_volume_identity.py#L67)
- [VolumeIdentityTests.test_rename_preserves_marker_history_and_folder_connections_after_restart](../../tests/test_volume_identity.py#L88)
- [VolumeIdentityTests.test_rename_rejects_offline_unregistered_and_duplicate_disks](../../tests/test_volume_identity.py#L123)
- [VolumeIdentityTests.test_failed_rename_leaves_original_marker_intact_and_removes_temporary](../../tests/test_volume_identity.py#L142)
- [VolumeIdentityTests.test_rename_rejects_changed_identity_symlink_and_invalid_names](../../tests/test_volume_identity.py#L153)
- [VolumeIdentityTests.test_concurrent_marker_change_is_not_overwritten](../../tests/test_volume_identity.py#L171)
- [VolumeIdentityTests.test_rename_api_validates_requests_and_updates_the_same_volume](../../tests/test_volume_identity.py#L192)
- [VolumeIdentityTests.test_unregistered_disk_does_not_use_legacy_share_history](../../tests/test_volume_identity.py#L218)
- [VolumeIdentityTests.test_identity_rechecked_before_and_after_directory_read](../../tests/test_volume_identity.py#L244)
- [VolumeIdentityTests.test_swap_during_read_rejects_result](../../tests/test_volume_identity.py#L259)
- [VolumeIdentityTests.test_duplicate_markers_block_both_mounts](../../tests/test_volume_identity.py#L267)
- [VolumeIdentityTests.test_capacity_keeps_last_successful_measurement_offline_and_on_failure](../../tests/test_volume_identity.py#L279)
- [VolumeIdentityTests.test_registration_refuses_existing_file_and_symlink_without_overwrite](../../tests/test_volume_identity.py#L298)
- [VolumeIdentityTests.test_invalid_oversized_or_special_marker_never_becomes_verified](../../tests/test_volume_identity.py#L308)
- [VolumeIdentityTests.test_capacity_uses_all_free_blocks_and_reports_user_available_separately](../../tests/test_volume_identity.py#L317)
- [VolumeIdentityTests.test_remembered_usb_resource_does_not_alias_legacy_disk](../../tests/test_volume_identity.py#L326)
- [VolumeIdentityTests.test_marker_is_excluded_from_comparison_inventory](../../tests/test_volume_identity.py#L338)

## `test_workspace_photos.py`

Виртуальные медиатеки в общих панелях.

- [WorkspacePhotosTests.test_library_button_opens_the_active_tree_without_changing_preview_mode](../../tests/test_workspace_photos.py#L9)
- [WorkspacePhotosTests.test_photos_browse_never_uses_mounted_directory_or_comparison_apis](../../tests/test_workspace_photos.py#L21)

## `test_workspace_refresh.py`

Обновление UI без потери дерева.

- [WorkspaceRefreshTests.test_capacity_poll_preserves_existing_disk_and_photos_trees](../../tests/test_workspace_refresh.py#L30)
- [WorkspaceRefreshTests.test_volume_access_change_updates_only_the_affected_tree](../../tests/test_workspace_refresh.py#L41)
- [WorkspaceRefreshTests.test_explicit_volume_refresh_can_redraw_both_trees](../../tests/test_workspace_refresh.py#L48)
- [WorkspaceRefreshTests.test_background_polling_stops_until_the_same_client_reconnects](../../tests/test_workspace_refresh.py#L54)

## `test_workspace_state.py`

Нормализация и восстановление состояния вкладки.

- [WorkspaceStateTests.test_navigation_snapshot_omits_file_lists_and_preserves_paths](../../tests/test_workspace_state.py#L22)
- [WorkspaceStateTests.test_invalid_saved_paths_and_identifiers_are_ignored](../../tests/test_workspace_state.py#L30)
- [WorkspaceStateTests.test_running_snapshot_does_not_invent_collapsed_folders_before_rows_exist](../../tests/test_workspace_state.py#L41)
- [WorkspaceRestoreTests.test_running_report_is_read_without_starting_resuming_or_pausing_a_job](../../tests/test_workspace_state.py#L58)
- [WorkspaceRestoreTests.test_reload_during_create_response_recovers_the_created_job_once](../../tests/test_workspace_state.py#L68)
- [WorkspaceRestoreTests.test_plain_panels_restore_both_roots_and_the_selected_file](../../tests/test_workspace_state.py#L80)
- [PairProgressViewTests.test_polling_the_same_running_report_preserves_both_paths_and_file_selection](../../tests/test_workspace_state.py#L94)
- [PairProgressViewTests.test_restored_navigation_waits_for_rows_without_changing_the_report](../../tests/test_workspace_state.py#L107)
