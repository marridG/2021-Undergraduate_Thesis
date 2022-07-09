# 2021-Undergraduate-Thesis

## File Tree


<details>
<summary>File Tree</summary>

```
📦Undergraduate Thesis                      // root directory `~/`
 ┣ 📂design_analysis                       // [DIRECTORY] general encoding design analysis (w.r.t. bars, distances, etc.)
 ┃ ┣ 📂__deprecated__                     // [DIRECTORY] deprecated implementations (wrapped in ~/design_analysis/*.py) 
 ┃ ┃ ┣ 📜2_by_1_encoding_2_per_bar.py    // deprecated
 ┃ ┃ ┣ 📜2_by_4_encoding_2_per_bar.py    // deprecated
 ┃ ┃ ┣ 📜2_by_5_encoding_1_per_bar.py    // deprecated
 ┃ ┃ ┗ 📜max_distance_calculation.py     // deprecated
 ┃ ┣ 📜level_1_duplicate_check.py         // check for possible duplicate sampling results of the level-1 encodings, by means of numerical simulation (iteratively select starting location values and/or sample points margin values) (with examples in `__main__`)
 ┃ ┗ 📜max_dist_cal.py                    // general calculator for the theoretically-possible level-1/2 encoding maximum working ranges (with examples in `__main__`)
 ┣ 📂detection                             // [DIRECTORY] detection, which: (1) extract sample points that fall on the encoding-embedded traffic sign boards, out tof the raw LiDAR point cloud data; and then (2) post-process to acquire a matrix-like binary representation that can be further used to complete the decoding operations
 ┃ ┣ 📂data_prep                          // [DIRECTORY] data preparation, i.e., to convert `.csv` files (exported from the `.pcap` LiDAR files through RoboSense RSView) to `.pcd` files and further to `.bin` files (shared by CYX) ([ALERT] some dependencies rely on `pcd2bin2` conda virtual environment on the 9991 server)
 ┃ ┃ ┣ 📂bin                             // [DIRECTORY] converted `.bin` files
 ┃ ┃ ┃ ┗ 📂seq60
 ┃ ┃ ┃ ┃ ┣ 📜seq60_00000__320.bin       // sequence #1/#6 (file `2021-10-27-19-11-43-RS-32-Data.pcap`, filename omitted below), frame 320
 ┃ ┃ ┃ ┃ ┣ 📜seq60_00000__321.bin       // sequence #1/#6, frame 321
 ┃ ┃ ┃ ┃ ┗ 📜seq60_00000__322.bin       // sequence #1/#6, frame 322
 ┃ ┃ ┣ 📂csv                              // [DIRECTORY] exported `.csv` files
 ┃ ┃ ┃ ┣ 📜2021-10-27-19-11-43-RS-32-Data (Frame 0320).csv
 ┃ ┃ ┃ ┣ 📜2021-10-27-19-11-43-RS-32-Data (Frame 0321).csv
 ┃ ┃ ┃ ┣ 📜2021-10-27-19-11-43-RS-32-Data (Frame 0322).csv
 ┃ ┃ ┃ ┗ 📜2021-10-27-19-11-43-RS-32-Data.pcap
 ┃ ┃ ┣ 📂seq60                            // [DIRECTORY] converted `.pcd` files
 ┃ ┃ ┃ ┣ 📜320.pcd                       // sequence #1/#6, frame 320
 ┃ ┃ ┃ ┣ 📜321.pcd                       // sequence #1/#6, frame 321
 ┃ ┃ ┃ ┗ 📜322.pcd                       // sequence #1/#6, frame 322
 ┃ ┃ ┣ 📜csv2trackerRes.sh                // bash script to execute on the 9991 server (just for reference)
 ┃ ┃ ┣ 📜loadtypicalCSV.py                // script to convert `.csv` to `.pcd` ([NOTE] check the floating point accuracy and intensity normalization operations)
 ┃ ┃ ┗ 📜pcd2bin.py                       // script to convert `.pcd` to `.bin` ([ALERT] some dependencies rely on `pcd2bin2` conda virtual environment on the 9991 server)
 ┃ ┗ 📂my_detection                        // [DIRECTORY] detection operations
 ┃ ┃ ┣ 📂data                             // data files
 ┃ ┃ ┃ ┣ 📜0001.pcd                      // can be ignored
 ┃ ┃ ┃ ┣ 📜seq60_00000__1-320.bin        // sequence #1/#6, frame 320
 ┃ ┃ ┃ ┣ 📜seq60_00000__1-321.bin        // sequence #1/#6, frame 320
 ┃ ┃ ┃ ┣ 📜seq60_00000__1-322.bin        // sequence #1/#6, frame 320
 ┃ ┃ ┃ ┣ 📜seq60_00000__3-268.bin        // sequence #3/#6 (file `2021-10-27-19-14-57-RS-32-Data.pcap`, filename omitted below), frame 268
 ┃ ┃ ┃ ┗ 📜seq60_00000__3-297.bin        // sequence #3/#6, frame 297
 ┃ ┃ ┣ 📂plot_binary                      // [DIRECTORY] scripts to plot the binarized matrix-like representation of the traffic sign board sample points
 ┃ ┃ ┃ ┣ 📜binarized-old.png             // old example figure
 ┃ ┃ ┃ ┣ 📜binarized.png                 // example figure
 ┃ ┃ ┃ ┣ 📜binary.npy                    // data of the example representation
 ┃ ┃ ┃ ┗ 📜plot_binary.py                // script
 ┃ ┃ ┣ 📂tests                            // [DIRECTORY] some test scripts (omitted in version control)
 ┃ ┃ ┃ ┣ 📜cluster_dbscan.py             // generate clusters in the raw LiDAR point cloud, by means of DBSCAN
 ┃ ┃ ┃ ┣ 📜cluster_euclidean.py          // [todo] [copied from web] generate clusters in the raw LiDAR point cloud, according to the euclidean distances between points
 ┃ ┃ ┃ ┣ 📜cluster_euclidean_kdtree.py   // [todo] [copied from web] generate clusters in the raw LiDAR point cloud, according to the euclidean distances between points and using KD-tree
 ┃ ┃ ┃ ┣ 📜plane_open3d.py               // fit a plane for the given points, using `open3d` APIs
 ┃ ┃ ┃ ┣ 📜plane_sklearn-1.py            // [todo] fit a plane for the given points, using `sklearn` APIs (approach 1)
 ┃ ┃ ┃ ┣ 📜plane_sklearn-2.py            // [todo] fit a plane for the given points, using `sklearn` APIs (approach 1)
 ┃ ┃ ┃ ┣ 📜points.npy                    // points (which can be generally regarded as all those fall on the encoding-embedded traffic sign) for plane fitting
 ┃ ┃ ┃ ┣ 📜points_on_board_2d_distribution.py
 ┃ ┃ ┃ ┣ 📜points_on_board_3d_distribution.py
 ┃ ┃ ┃ ┣ 📜points_on_off_board.py
 ┃ ┃ ┃ ┣ 📜points_proj_dup_cnt.npy
 ┃ ┃ ┃ ┣ 📜points_xyz_off_board.npy
 ┃ ┃ ┃ ┣ 📜points_xyz_on_board.npy
 ┃ ┃ ┃ ┣ 📜projection_example.py
 ┃ ┃ ┃ ┣ 📜range_data.npy
 ┃ ┃ ┃ ┣ 📜show_points_dup_cnt.py
 ┃ ┃ ┃ ┗ 📜show_range_image.py
 ┃ ┃ ┣ 📂utils
 ┃ ┃ ┃ ┣ 📂pt_cloud_color_bar
 ┃ ┃ ┃ ┣ 📜BV_1440.json
 ┃ ┃ ┃ ┣ 📜camera-plate.json
 ┃ ┃ ┃ ┣ 📜camera_option-old.json
 ┃ ┃ ┃ ┣ 📜camera_option.json
 ┃ ┃ ┃ ┗ 📜open3d_view.py
 ┃ ┃ ┣ 📜board_extractor.py
 ┃ ┃ ┣ 📜data_loader.py
 ┃ ┃ ┣ 📜do_extraction.py
 ┃ ┃ ┣ 📜plane_projection.py
 ┃ ┃ ┣ 📜points_xyz_off_board.npy
 ┃ ┃ ┣ 📜points_xyz_on_board.npy
 ┃ ┃ ┣ 📜point_cloud_visualization.py
 ┃ ┃ ┗ 📜test.py
 ┣ 📂environment
 ┃ ┣ 📜IP Settings.PNG
 ┃ ┣ 📜Restore IP Address to DHCP.bat
 ┃ ┗ 📜Set IP Address.bat
 ┣ 📂simulation
 ┃ ┣ 📂analysis
 ┃ ┃ ┣ 📜advanced_property_search.py
 ┃ ┃ ┣ 📜lidar_resolution_analysis.py
 ┃ ┃ ┣ 📜sample_cnt_analysis.py
 ┃ ┃ ┣ 📜sample_cnt_analysis__avg.png
 ┃ ┃ ┣ 📜sample_cnt_analysis__cnt_cnt_cat.png
 ┃ ┃ ┣ 📜sample_cnt_analysis__max.png
 ┃ ┃ ┗ 📜sample_cnt_analysis__min.png
 ┃ ┣ 📂data_v1
 ┃ ┃ ┣ 📜classification.png
 ┃ ┃ ┣ 📜constants.py
 ┃ ┃ ┗ 📜taffic_signs.py
 ┃ ┣ 📂data_v2
 ┃ ┃ ┣ 📜constants.py
 ┃ ┃ ┗ 📜taffic_signs.py
 ┃ ┣ 📂encoding_v1_1
 ┃ ┃ ┣ 📜encode_v1_1.py
 ┃ ┃ ┗ 📜__init__.py
 ┃ ┣ 📂encoding_v1_2
 ┃ ┃ ┣ 📜decode_v1_2.py
 ┃ ┃ ┣ 📜encode_v1_2.py
 ┃ ┃ ┣ 📜pattern_v1_2.py
 ┃ ┃ ┣ 📜substring_match_BM.py
 ┃ ┃ ┗ 📜__init__.py
 ┃ ┣ 📂encoding_v2_1
 ┃ ┃ ┣ 📜back_trace_min_ex.py
 ┃ ┃ ┣ 📜decode_v2_1_ver1.py
 ┃ ┃ ┣ 📜decode_v2_1_ver2_0.py
 ┃ ┃ ┣ 📜decode_v2_1_ver2_1.py
 ┃ ┃ ┣ 📜decode_v2_1_ver3.py
 ┃ ┃ ┣ 📜encode_v2_1.py
 ┃ ┃ ┣ 📜pattern_v2_1.py
 ┃ ┃ ┣ 📜substring_match_BM.py
 ┃ ┃ ┗ 📜__init__.py
 ┃ ┣ 📂tests
 ┃ ┃ ┣ 📂canvas_img
 ┃ ┃ ┃ ┣ 📜canvas_v1_1.png
 ┃ ┃ ┃ ┣ 📜canvas_v1_2.png
 ┃ ┃ ┃ ┣ 📜canvas_v2_1.png
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__cir00.png
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__cir01.png
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__cir10.png
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__cir11.png
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__rect00.png
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__rect01.png
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__rect10.png
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__rect11.png
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__tri00.png
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__tri01.png
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__tri10.png
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__tri11.png
 ┃ ┃ ┃ ┗ 📜canvas_v3__cir01.png
 ┃ ┃ ┣ 📜canvas_v3__cir01.png
 ┃ ┃ ┣ 📜plot_binary.py
 ┃ ┃ ┣ 📜sample.npy
 ┃ ┃ ┣ 📜sample_binarized.png
 ┃ ┃ ┣ 📜test_encoding_v1_1.py
 ┃ ┃ ┣ 📜test_encoding_v1_2.py
 ┃ ┃ ┣ 📜test_encoding_v2_1_ver1.py
 ┃ ┃ ┣ 📜test_encoding_v2_1_ver2_0.py
 ┃ ┃ ┣ 📜test_encoding_v2_1_ver2_1.py
 ┃ ┃ ┗ 📜test_encoding_v2_1_ver3.py
 ┃ ┣ 📂tests_plots
 ┃ ┃ ┣ 📂plots
 ┃ ┃ ┣ 📜draw.py
 ┃ ┃ ┣ 📜raw_results-before avlid debug.txt
 ┃ ┃ ┣ 📜raw_results.txt
 ┃ ┃ ┗ 📜raw_results_v3.txt
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜exceptions.cpython-37.pyc
 ┃ ┃ ┣ 📜lidar_points.cpython-37.pyc
 ┃ ┃ ┣ 📜sign_boards.cpython-37.pyc
 ┃ ┃ ┣ 📜utils.cpython-37.pyc
 ┃ ┃ ┗ 📜visualization.cpython-37.pyc
 ┃ ┣ 📜exceptions.py
 ┃ ┣ 📜lidar_points.py
 ┃ ┣ 📜sign_boards.py
 ┃ ┣ 📜test.py
 ┃ ┣ 📜utils.py
 ┃ ┗ 📜visualization.py
 ┣ 📜.gitignore
 ┗ 📜README.md
```

</details>