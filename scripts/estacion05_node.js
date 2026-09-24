const crypto = require('crypto');
const { Client, Message } = require('azure-iot-device');
const { Mqtt } = require('azure-iot-device-mqtt');
const { ProvisioningDeviceClient } = require('azure-iot-provisioning-device');
const { Mqtt: ProvMqtt } = require('azure-iot-provisioning-device-mqtt');
const { SymmetricKeySecurityClient } = require('azure-iot-security-symmetric-key');

const ID = 'estacion-campo-01';
const INTERVALO = 300 * 1000;
const scope = process.env.IOTC_ID_SCOPE;
const claveGrupo = process.env.IOTC_GROUP_KEY;

const clave = crypto.createHmac('sha256', Buffer.from(claveGrupo, 'base64')).update(ID).digest('base64');

function horaLocal() {
  const d = new Date(Date.now() - 5 * 3600 * 1000);
  return d.getUTCHours() + d.getUTCMinutes() / 60;
}

const CADA = 260 * 60 * 1000;
const DURA = 35 * 60 * 1000;
const DESFASE = 7 * 3600 * 1000;

function apagon() {
  return (Date.now() + DESFASE) % (CADA + DURA) >= CADA;
}

function leer() {
  const h = horaLocal();
  const tarde = h > 13 && h < 18;
  const llueve = Math.random() < (tarde ? 0.25 : 0.04);
  const lluvia = llueve ? Math.round(Math.random() * 6) * 0.2 : 0;
  const foliar = llueve ? 85 + Math.random() * 15 : Math.max(5, 45 - Math.abs(h - 13) * 4 + Math.random() * 10);
  return { lluviaLote: Number(lluvia.toFixed(1)), humedadFoliar: Number(foliar.toFixed(1)) };
}

const seguridad = new SymmetricKeySecurityClient(ID, clave);
const prov = ProvisioningDeviceClient.create('global.azure-devices-provisioning.net', scope, new ProvMqtt(), seguridad);

prov.register((err, resultado) => {
  if (err) {
    console.log('registro fallido', err.message);
    process.exit(1);
  }
  const cadena = `HostName=${resultado.assignedHub};DeviceId=${resultado.deviceId};SharedAccessKey=${clave}`;
  const cliente = Client.fromConnectionString(cadena, Mqtt);
  cliente.open((e) => {
    if (e) {
      console.log('conexion fallida', e.message);
      process.exit(1);
    }
    console.log('conectado');
    let abierto = true;
    setInterval(() => {
      if (apagon()) {
        if (abierto) {
          abierto = false;
          cliente.close(() => console.log('desconectado'));
        }
        return;
      }
      if (!abierto) {
        cliente.open((er) => {
          if (!er) {
            abierto = true;
            console.log('reconectado');
          }
        });
        return;
      }
      const datos = leer();
      const msg = new Message(JSON.stringify(datos));
      msg.contentType = 'application/json';
      msg.contentEncoding = 'utf-8';
      cliente.sendEvent(msg, (er) => console.log(er ? 'error ' + er.message : JSON.stringify(datos)));
    }, INTERVALO);
  });
});
