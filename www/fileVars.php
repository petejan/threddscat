<?php

include 'db.php';

$connectString = 'host=' . $host . ' port=' . $port . ' dbname=' . $database .  ' user=' . $user . ' password=' . $password;

$link = pg_connect ($connectString);
if (!$link)
{
	die('Error: Could not connect: ' . pg_last_error());
}

$query = 'SELECT file_id, url, variable, variable, name, units, depth, dimensions, aux_vars FROM parameters JOIN file USING (file_id)';

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
	if ($i > 2)
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
			$u = $c_row;
		else if ($y == 2)
			$v = $c_row;
		else if ($y == 3)
			echo '<small><td><a href=aodn.php?file_id='. $id . '&var=' . $v . '&url=' . $u . '  target="_blank">' . $c_row . '<a></td></small>';
		else
			echo '<small><td>' . $c_row . '</td></small>';
		next($row);
		$y = $y + 1;
	}
	echo '</tr>';
	$i = $i + 1;
}
echo "</table>";

pg_free_result($result);
?>
