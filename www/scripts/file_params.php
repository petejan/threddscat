<?php

/*
 * DataTables example server-side processing script.
 *
 * Please note that this script is intentionally extremely simply to show how
 * server-side processing can be implemented, and probably shouldn't be used as
 * the basis for a large complex system. It is suitable for simple use cases as
 * for learning.
 *
 * See http://datatables.net/usage/server-side for full details on the server-
 * side processing requirements of DataTables.
 *
 * @license MIT - http://datatables.net/license_mit
 */

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * Easy set variables
 */

// DB table to use
$table = 'file_params';

// Table's primary key
$primaryKey = 'file_id';

date_default_timezone_set('UTC');

// Array of database columns which should be read and sent back to DataTables.
// The `db` parameter represents the column name in the database, while the `dt`
// parameter represents the DataTables column identifier. In this case simple
// indexes
$columns = array(
    array( 'db' => 'file_id', 'dt' => 'file_id' ),
    array( 'db' => 'site_code', 'dt' => 'site_code' ),
    array( 'db' => 'platform_code',  'dt' => 'platform_code' ),
    array( 'db' => 'deployment_code',   'dt' => 'deployment_code' ),
    array( 'db' => 'time_deployment_start',     'dt' => 'time_deployment_start' ,
            'formatter' => function( $d, $row ) { return date( 'Y-m-d', strtotime($d)); }
	       ),
    array( 'db' => 'file_name',     'dt' => 'file_name' ),
    array( 'db' => 'params',     'dt' => 'params' ),
    array( 'db' => 'url',     'dt' => 'url' ),
);

// SQL server connection information
$sql_details = array(
    'user' => 'petejan1_ddb',
    'pass' => 'dbpassword1234',
    'db'   => 'petejan1_thredds',
    'host' => 'localhost'
);


/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * If you just want to use the basic configuration for DataTables with PHP
 * server-side, there is no need to edit below this line.
 */

require( 'ssp.class.php' );

echo json_encode(
    SSP::simple( $_GET, $sql_details, $table, $primaryKey, $columns )
);