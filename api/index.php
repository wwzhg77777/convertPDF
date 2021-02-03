<?php
header('Access-Control-Allow-Origin:*');
header('Access-Control-Allow-Methods:GET,POST,OPTIONS');
header('Access-Control-Allow-Headers:Origin, X-Requested-With, Content-Type');

if (isset($_GET['a']) && isset($_GET['t'])) {
    $app_id = $_GET['a'];
    $unix_ontime = $_GET['t'];

    $conn = @mysqli_connect('127.0.0.1', 'root', 'root', 'pdfrecord', 3306, '');
    $input = array(
        'errCode' => '',
        'count' => null,
        'message' => ''
    );

    if (mysqli_connect_error()) {
        $input['errCode'] = 403;
        $input['count'] = null;
        $input['message'] = '连接数据库失败';
        print_r(json_encode($input));
    } else {
        $query = "SELECT * FROM
            `index` WHERE
            `app_id`='$app_id'";
        $result = $conn->query($query);

        # 不存在则新建数据
        if (mysqli_num_rows($result) != 2) {
            $insertsql = "INSERT INTO `index`
            (`app_id`,`type`,`count`,`unix_time`) VALUES ";
            $conn->query($insertsql . "('$app_id','basicAccurate','0',UNIX_TIMESTAMP(NOW()))");
            $conn->query($insertsql . "('$app_id','basicGeneral','0',UNIX_TIMESTAMP(NOW()))");
            # 更新查询集
            $result = $conn->query($query);
        }

        $rows = array();
        # 获取查询的数据
        while ($row = mysqli_fetch_assoc($result)) {
            if ($row['type'] == 'basicAccurate') {
                $rows[0] = $row;
            } else {
                $rows[1] = $row;
            }
        }
        # 返回查询到的数据
        $input['errCode'] = 0;
        $input['count'] = array(
            'bA' => $rows[0]['count'],
            'bG' => $rows[1]['count']
        );
        $input['message'] = 'success';
        print_r(json_encode($input));
    }
    mysqli_close($conn);
    exit;
}

if (isset($_POST)) {
    $postData = file_get_contents('php://input');
    $Data = !empty($postData) ? json_decode($postData, true) : array();

    if (isset($Data['nf'])) {
        $nf = " & {$Data['nf']}";
    } else {
        $nf = "";
    }

    if (empty($Data)) {
        $input['errCode'] = 404;
        $input['count'] = null;
        $input['message'] = '未接收到数据';
        print_r(json_encode($input));
    } else {
        $conn = @mysqli_connect('127.0.0.1', 'root', 'root', 'pdfrecord', 3306, '');
        $input = array(
            'errCode' => '',
            'count' => null,
            'message' => '',
            'type' => ''
        );

        if (mysqli_connect_error()) {
            $input['errCode'] = 403;
            $input['count'] = null;
            $input['message'] = '连接数据库失败';
            print_r(json_encode($input));
        } else {
            $query = "SELECT * FROM
            `index` WHERE
            `app_id`='{$Data['a']}'";
            $result = $conn->query($query);

            # 不存在则新建数据
            if (mysqli_num_rows($result) != 2) {
                $insertsql = "INSERT INTO `index`
                (`app_id`,`type`,`count`,`unix_time`) VALUES ";
                $conn->query($insertsql . "('{$Data['a']}','basicAccurate','0',UNIX_TIMESTAMP(NOW()))");
                $conn->query($insertsql . "('{$Data['a']}','basicGeneral','0',UNIX_TIMESTAMP(NOW()))");
                # 更新查询集
                $result = $conn->query($query);
            }

            $rows = array();
            # 获取查询的数据
            while ($row = mysqli_fetch_assoc($result)) {
                if ($row['type'] == 'basicAccurate') {
                    $rows[0] = $row;
                } else {
                    $rows[1] = $row;
                }
            }
            # 检查并刷新当天的免费次数
            if (strtotime(date('Ymd')) > $rows[0]['unix_time']) {
                # 当天0点的时间戳 > 已用识别记录的时间戳 :  记录是昨天的，需要刷新当天次数
                $c_str = "UPDATE `index` SET
                `count`=0 WHERE
                `app_id`='{$Data['a']}' AND";
                $conn->query($c_str . " `type`='basicAccurate'");
                $conn->query($c_str . " `type`='basicGeneral'");

                # 更新查询集
                $rows[0]['count'] = 0;
                $rows[1]['count'] = 0;
            }

            $sql = "UPDATE `index` SET
            `count`=`count`+1 ,
            `unix_time`=UNIX_TIMESTAMP(NOW()) WHERE
            `app_id`='{$Data['a']}' AND";
            $str = "";

            # 当天次数用完
            if ($rows[0]['count'] >= 500 && $rows[1]['count'] >= 50000) {
                $input['errCode'] = 210;
                $input['count'] = 50000;
                $input['message'] = '次数用光了';
                print_r(json_encode($input));
                exit;
            }
            # 当天次数未用完
            if ($rows[0]['count'] >= 500) {
                $str = "basicGeneral";
                $input['count'] = array(
                    'bA' => $rows[0]['count'],
                    'bG' => $rows[1]['count'] + 1
                );
            } else {
                $str = "basicAccurate";
                $input['count'] = array(
                    'bA' => $rows[0]['count'] + 1,
                    'bG' => $rows[1]['count']
                );
            }

            # 执行自增函数, 返回已用次数
            if ($conn->query($sql . "`type`='$str'")) {
                $input['errCode'] = 0;
                $input['message'] = 'success';
                $input['type'] = $str;
                print_r(json_encode($input));

                # (可选) 记录识别的文件和大小
                $filesize_mb = substr($Data['filesize'] / 1024 / 1024, 0, 4);
                $recordstr = "INSERT INTO `record`
                (`filename`,`filesize`,`app_id`,`type`,`unix_time`) VALUES
                ('{$Data['filename']}$nf','$filesize_mb','{$Data['a']}','$str',UNIX_TIMESTAMP(NOW()))";
                $conn->query($recordstr);
            }
        }
        mysqli_close($conn);
    }
}
