# After The Swarm

**Point Value**: 973 pts
**Author: @vvanuss**

## Description

hard
We obtained a large network capture of an infected IoT device.
You need to reconstruct not a single artifact, but three linked stages of the infection chain:
The start of the first mass propagation wave on 8081/tcp.
The only HTTP object requested after that wave had already started.
The first successful 4554/tcp control-exchange that happened after that late HTTP request.
Then recover:
The name of the late HTTP object.
The source TCP port of that HTTP request.
The source TCP port of the control session.
The size of the first client payload in that control session.
The sizes of the first three server payloads in the same session.
Flag:
Format: grodno{artifact_httpport_c2port_c2len_s2len1_s2len2_s2len3}
Example: grodno{arm_44444_55555_00_00_0_0}
Мы получили объемный дамп сетевого трафика зараженного IoT-устройства.
Вам необходимо восстановить не один отдельный артефакт, а три взаимосвязанных этапа цепочки заражения:
Момент начала первой массовой propagation-волны на 8081/tcp.
Единственный HTTP-объект, который был запрошен уже после начала этой волны.
Первый успешный control-exchange по 4554/tcp, который произошёл уже после этого позднего HTTP-запроса.
Затем определите:
Имя позднего HTTP-объекта.
Исходный TCP-порт этого HTTP-запроса.
Исходный TCP-порт control-сессии.
Размер первого полезного сообщения клиента в control-сессии.
Размеры трёх первых полезных сообщений сервера в этой же сессии.
Флаг:
Формат: grodno{artifact_httpport_c2port_c2len_s2len1_s2len2_s2len3}
Пример: grodno{arm_44444_55555_00_00_0_0}
Download Attachment
External Link
You've tried 0 times already!

