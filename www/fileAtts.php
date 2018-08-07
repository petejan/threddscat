<?php

include 'db.php';

$connectString = 'host=' . $host . ' port=' . $port . ' dbname=' . $database .  ' user=' . $user . ' password=' . $password;

$link = pg_connect ($connectString);
if (!$link)
{
	die('Error: Could not connect: ' . pg_last_error());
}

$query = 'SELECT file_id, name AS global_attribute, value FROM global_attributes ';

if(isset($_POST['file_id']))
{
	$query = $query . ' WHERE file_id = ' . $_POST['file_id'] . ' ';
}
$query = $query . 'ORDER BY name';

$result = pg_query($query);
echo "<table>";

$i = 0;
echo "<tr>";
while ($i < pg_num_fields($result))
{
	$fieldName = pg_field_name($result, $i);
	if ($i > 0)
		echo '<td><b>' . $fieldName . '</b></td>';
	$i = $i + 1;
}
echo '</tr>';
$i = 0;

while ($row = pg_fetch_row($result))
{
	print "<tr class=\"d".($i & 1)."\">";
	$count = count($row);
	$y = 0;
	while ($y < $count)
	{
		$c_row = current($row);
		if ($y == 0)
			$id = $c_row;
		else if ($y == 1)
			echo '<small><td><a href=fileParams.php?file_id=' . $id . '>' . $c_row . '<a></td></small>';
		else
			echo '<small><td>' . nl2br($c_row) . '</td></small>';
		next($row);
		$y = $y + 1;
	}
	echo '</tr>';
	$i = $i + 1;
}
echo "</table>";
pg_free_result($result);
?>
