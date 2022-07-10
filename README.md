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
 ┃ ┣ 📜level_1_duplicate_check.py         // [class-oriented] check for possible duplicate sampling results of the level-1 encodings, by means of numerical simulation (iteratively select starting location values and/or sample points margin values) (with examples in `__main__`)
 ┃ ┗ 📜max_dist_cal.py                    // [class-oriented] general calculator for the theoretically-possible level-1/2 encoding maximum working ranges (with examples in `__main__`)
 ┣ 📂detection                             // [DIRECTORY] detection, which: (1) extract sample points that fall on the encoding-embedded traffic sign boards, out of the raw LiDAR point cloud data; and then (2) post-process to acquire a matrix-like binary representation that can be further used to complete the decoding operations. ([NOTE] unless specified, all scripts/settings are for sequence #1/#6, frame 320/321/322)
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
 ┃ ┃ ┃ ┃                                 // visualize the 2d-distribution (w.r.t. fit line) of the given points, with z-axis removed
 ┃ ┃ ┃ ┣ 📜points_on_board_3d_distribution.py
 ┃ ┃ ┃ ┃                                 // [todo] visualize the 3d-distribution (w.r.t. fit plane) of the given points
 ┃ ┃ ┃ ┣ 📜points_on_off_board.py        // scripts to check whether: (1) all off-board points are mapped to range image pixels `P`; (2) there exist some on-board points that map to each range image pixel `p \in P`
 ┃ ┃ ┃ ┣ 📜points_proj_dup_cnt.npy       // a matrix of a size the same as the range image, where each element is the number of points (in the raw point cloud) that are mapped to the range image pixel at the corresponding location
 ┃ ┃ ┃ ┣ 📜points_xyz_off_board.npy      // all off-board points (selected by empirical coordinates threshold criterions)
 ┃ ┃ ┃ ┣ 📜points_xyz_on_board.npy       // all on-board points (selected by empirical coordinates threshold criterions)
 ┃ ┃ ┃ ┣ 📜projection_example.py         // [todo] [copied from web] some seemingly-working plane projection codes
 ┃ ┃ ┃ ┣ 📜range_data.npy                // range image data
 ┃ ┃ ┃ ┣ 📜show_points_dup_cnt.py        // visualize the representing image of file `points_proj_dup_cnt.npy`
 ┃ ┃ ┃ ┗ 📜show_range_image.py           // visualize the representing range image of file `range_data.npy`
 ┃ ┃ ┣ 📂utils                            // [DIRECTORY] opne3d-oriented 3d point cloud visualization: reference scripts, setting files, etc.
 ┃ ┃ ┃ ┣ 📂pt_cloud_color_bar            // [DIRECTORY] images of the color bars used while visualizing point clouds by the intensity of each point
 ┃ ┃ ┃ ┣ 📜BV_1440.json                  // can be neglected
 ┃ ┃ ┃ ┣ 📜camera-plate.json             // camera settings (angle of view) used while visualizing traffic sign board points
 ┃ ┃ ┃ ┣ 📜camera_option-old.json        // can be neglected
 ┃ ┃ ┃ ┣ 📜camera_option.json            // camera settings (angle of view) used while visualizing the entire raw point cloud
 ┃ ┃ ┃ ┗ 📜open3d_view.py                // [copied from web] reference codes to: (1) create camera settings; (2) use existing camera settings
 ┃ ┃ ┣ 📜board_extractor.py               // scripts to extract all the sample points that fall on encoding-embedded traffic sign boards, out of the entire point cloud
 ┃ ┃ ┣ 📜data_loader.py                   // `.bin` point cloud file data loader 
 ┃ ┃ ┣ 📜do_extraction.py                 // entry scripts for the detection operations
 ┃ ┃ ┣ 📜plane_projection.py              // scripts to post-process the extracted points (that fall on the encoding-embedded traffic sign boards), so as to acquire the matrix-like binary representation
 ┃ ┃ ┣ 📜point_cloud_visualization.py     // utilities for visualizing point cloud data
 ┃ ┃ ┗ 📜test.py                          // can be ignored
 ┣ 📂environment                            // environment setting scripts for RoboSense LiDAR device
 ┃ ┣ 📜IP Settings.PNG                     // demonstration of the required static IP address settings
 ┃ ┣ 📜Restore IP Address to DHCP.bat      // scripts to restore static IP address to DHCP
 ┃ ┗ 📜Set IP Address.bat                  // set IP address to the required static one
 ┣ 📂simulation                             // [DIRECTORY] simulation: (1) traffic sign board contents => categorized (level-1/2/3) indices; (2) categorized indices => embedded encodings to be placed onto traffic sign boards of the corresponding shapes; (3) sample at different distances; (4) w.r.t. the sampled results, attempt to decode, so as to extract the corresponding traffic sign contents
 ┃ ┣ 📂analysis                             // [DIRECTORY] analyze sampling properties or encoding designs
 ┃ ┃ ┣ 📜advanced_property_search.py       // [todo] scripts to search for encoding designs with advanced properties
 ┃ ┃ ┣ 📜lidar_resolution_analysis.py      // scripts to analyze the line resolution of LiDAR at different distances
 ┃ ┃ ┣ 📜sample_cnt_analysis.py            // scripts to analyze the difference of the number of sample points that fall on each bar (more specifically, adjacent bars) of the encodings
 ┃ ┃ ┣ 📜sample_cnt_analysis__avg.png      // result image of `sample_cnt_analysis.py`: avergae difference
 ┃ ┃ ┣ 📜sample_cnt_analysis__cnt_cnt_cat.png
 ┃ ┃ ┣                                     // result image of `sample_cnt_analysis.py`: difference by value
 ┃ ┃ ┣ 📜sample_cnt_analysis__max.png      // result image of `sample_cnt_analysis.py`: maximum difference
 ┃ ┃ ┗ 📜sample_cnt_analysis__min.png      // result image of `sample_cnt_analysis.py`: minimum difference
 ┃ ┣ 📂data_v1                              // [DIRECTORY] VERSION-1 encoding schema of traffic sign board contents (i.e. contents => level-1/2/3 categorized indices)
 ┃ ┃ ┣ 📜classification.png                // Chinese traffic sign board classifications, from paper **Traffic-Sign Detection and Classification in the Wild__CVPR 2016*
 ┃ ┃ ┣ 📜constants.py                      // constants of the encoding schema
 ┃ ┃ ┗ 📜taffic_signs.py                   // [class-oriented] utilities of the encoding schema (with examples in `__main__`)
 ┃ ┣ 📂data_v2                              // [DIRECTORY] VERSION-2 encoding schema of traffic sign board contents (i.e. contents => level-1/2/3 categorized indices)
 ┃ ┃ ┣ 📜constants.py                      // constants of the encoding schema
 ┃ ┃ ┗ 📜taffic_signs.py                   // [class-oriented] utilities of the encoding schema (with examples in `__main__`)
 ┃ ┣ 📂encoding_v1_1                        // [DIRECTORY] [deprecated] VERSION-1-1 traffic sign board content indices => on-board embedded encodings
 ┃ ┃ ┣ 📜encode_v1_1.py                    // encoder scripts
 ┃ ┃ ┗ 📜__init__.py                       // to make it package alike
 ┃ ┣ 📂encoding_v1_2                        // [DIRECTORY] VERSION-1-2 traffic sign board content indices => on-board embedded encodings (3 levels)
 ┃ ┃ ┣ 📜decode_v1_2.py                    // decoder scripts
 ┃ ┃ ┣ 📜encode_v1_2.py                    // encoder scripts
 ┃ ┃ ┣ 📜pattern_v1_2.py                   // level-1 encoding patterns
 ┃ ┃ ┣ 📜substring_match_BM.py             // scripts for sub-string matching, by means of Boyer-Moore Algorithm
 ┃ ┃ ┗ 📜__init__.py                       // to make it package alike
 ┃ ┣ 📂encoding_v2_1                        // [DIRECTORY] [deprecated] VERSION-2-1 traffic sign board content indices => on-board embedded encodings (2 levels)
 ┃ ┃ ┣ 📜back_trace_min_ex.py              // minimum example of the back tracing method used in decoding
 ┃ ┃ ┣ 📜decode_v2_1_ver1.py               // decoder scripts version-1: can be ignored
 ┃ ┃ ┣ 📜decode_v2_1_ver2_0.py             // decoder scripts version-2-0: (1) brute force starting locations to extract points that fall on the encodings part only; (2) brute force starting locations to decode
 ┃ ┃ ┣ 📜decode_v2_1_ver2_1.py             // decoder scripts version-2-1: (1) back-trace to extract points that fall on the encodings part only; (2) brute force starting locations to decode
 ┃ ┃ ┣ 📜decode_v2_1_ver3.py               // decoder scripts version-3: (1) back-trace to extract points that fall on the encodings part only; (2) decode by the sample-point-to-binary-bit combining scehma deteremined by the back-tracing extraction results
 ┃ ┃ ┣ 📜encode_v2_1.py                    // encoder scripts
 ┃ ┃ ┣ 📜pattern_v2_1.py                   // level-1 encoding patterns
 ┃ ┃ ┣ 📜substring_match_BM.py             // scripts for sub-string matching, by means of Boyer-Moore Algorithm
 ┃ ┃ ┗ 📜__init__.py                       // to make it package alike
 ┃ ┣ 📂tests                                // [DIRECTORY] scripts to run simulations of all encoder & decoder implementation
 ┃ ┃ ┣ 📂canvas_img                        // [DIRECTORY] images of simulated traffic sign boards with embedded encodings
 ┃ ┃ ┃ ┣ 📜canvas_v1_1.png                // VERSION-1-1
 ┃ ┃ ┃ ┣ 📜canvas_v1_2.png                // VERSION-1-2
 ┃ ┃ ┃ ┣ 📜canvas_v2_1.png                // VERSION-2-1
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__cir00.png         // VERSION-2-1: circle (without scaled height; without optimal height:width ratio)
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__cir01.png         // VERSION-2-1: circle (without scaled height; with optimal height:width ratio)
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__cir10.png         // VERSION-2-1: circle (with scaled height; without optimal height:width ratio)
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__cir11.png         // VERSION-2-1: circle (with scaled height; with optimal height:width ratio)
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__rect00.png        // VERSION-2-1: rectangle (without scaled height; without optimal height:width ratio)
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__rect01.png        // VERSION-2-1: rectangle (without scaled height; with optimal height:width ratio)
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__rect10.png        // VERSION-2-1: rectangle (with scaled height; without optimal height:width ratio)
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__rect11.png        // VERSION-2-1: rectangle (with scaled height; with optimal height:width ratio)
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__tri00.png         // VERSION-2-1: triangke (without scaled height; without optimal height:width ratio)
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__tri01.png         // VERSION-2-1: triangke (without scaled height; with optimal height:width ratio)
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__tri10.png         // VERSION-2-1: triangke (with scaled height; without optimal height:width ratio)
 ┃ ┃ ┃ ┣ 📜canvas_v2_1__tri11.png         // VERSION-2-1: triangke (with scaled height; with optimal height:width ratio)
 ┃ ┃ ┃ ┗ 📜canvas_v3__cir01.png           // VERSION-3: circle (without scaled height; with optimal height:width ratio)
 ┃ ┃ ┣ 📜plot_binary.py                    // sciipts to plot the given sample results (all as binary pits)
 ┃ ┃ ┣ 📜sample.npy                        // example sample results
 ┃ ┃ ┣ 📜sample_binarized.png              // plot of `sample.npy` by `plot_binary.py`
 ┃ ┃ ┣ 📜test_encoding_v1_1.py             // entry scripts of running simulation for encoding schema VERSION-1-1
 ┃ ┃ ┣ 📜test_encoding_v1_2.py             // entry scripts of running simulation for encoding schema VERSION-1-2
 ┃ ┃ ┣ 📜test_encoding_v2_1_ver1.py        // entry scripts of running simulation for encoding schema VERSION-2-1, using decoder version-1
 ┃ ┃ ┣ 📜test_encoding_v2_1_ver2_0.py      // entry scripts of running simulation for encoding schema VERSION-2-1, using decoder version-2-0
 ┃ ┃ ┣ 📜test_encoding_v2_1_ver2_1.py      // entry scripts of running simulation for encoding schema VERSION-2-1, using decoder version-2-1
 ┃ ┃ ┗ 📜test_encoding_v2_1_ver3.py        // entry scripts of running simulation for encoding schema VERSION-2-1, using decoder version-2
 ┃ ┣ 📂tests_plots                          // [DIRECTORY] simulation result plots
 ┃ ┃ ┣ 📂plots                             // [DIRECTORY] simulation result plots
 ┃ ┃ ┣ 📜draw.py                           // scripts to plot simulation results
 ┃ ┃ ┣ 📜raw_results-before avlid debug.txt// can be ignored, old results
 ┃ ┃ ┣ 📜raw_results.txt                   // simulation results of encoding schema VERSION-2-1, using deocder version-2-0 and version-2-1
 ┃ ┃ ┗ 📜raw_results_v3.txt                // simulation results of encoding schema VERSION-2-1, using deocder version-3
 ┃ ┣ 📜exceptions.py                        // scripts implementing exceptions that will possibly occur during decoding
 ┃ ┣ 📜lidar_points.py                      // [class-oriented] scripts simulating LiDAR sampling at different distances (with examples in `__main__`)
 ┃ ┣ 📜sign_boards.py                       // [class-oriented] scripts simulating placing encodings onto traffic sign boards (with examples in `__main__`)
 ┃ ┣ 📜test.py                              // can be ignored
 ┃ ┣ 📜utils.py                             // scripts implementing some utilities
 ┃ ┗ 📜visualization.py                     // [class-oriented] scripts implementing the visulaization of encoding-embedded traffic sign boards (with examples in `__main__`)    
 ┣ 📜.gitignore                              // git ignore file
 ┗ 📜README.md                               // readme file
```

</details>