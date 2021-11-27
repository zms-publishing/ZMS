def getJSONEditor(self):
  frmu = self.ZMSFormulator(self)
  jsed = self.JSONEditor(frmu)
    
  # Google.API.sitekey.password not configured
  if frmu.GoogleAPIKey == 'no_site_key':
    output = '''
      <div id="editor_holder"></div>
      <button id="submit" class="btn btn-danger">%s</button>
      <button id="restore" class="btn btn-secondary">%s</button>
      <span id="valid_indicator"></span>
      <input id="captcha" type="hidden" />
      <br />
    '''%(self.getLangStr('ZMSFORMULATOR_BUTTON_SUBMIT',self.REQUEST.get('lang')), self.getLangStr('ZMSFORMULATOR_BUTTON_RESTORE',self.REQUEST.get('lang')))
  else:
    output = '''
      <div id="editor_holder"></div>
      <button id="submit" class="g-recaptcha button"
        style="height: 0px; width: 0px; border: none; padding: 0px;" hidefocus="true"
        data-callback="recaptchaCallback"
        data-badge="bottomleft"
        class="g-recaptcha"
        data-sitekey="%s"></button>
      <button id="captcha" onclick="validate_or_submit()">%s</button>
      <button id="restore">%s</button>
      <span id="valid_indicator"></span>
      <script src='https://www.google.com/recaptcha/api.js'></script>
      <script>
        function recaptchaCallback(){$('#submit').trigger('click');grecaptcha.reset();}
        function validate_or_submit(){if (grecaptcha.getResponse() ==""){grecaptcha.execute()}else{$('#submit').trigger('click')}}
      </script> 
      <br />
    '''%(frmu.GoogleAPIKey,self.getLangStr('ZMSFORMULATOR_BUTTON_SUBMIT',self.REQUEST.get('lang')),self.getLangStr('ZMSFORMULATOR_BUTTON_RESTORE',self.REQUEST.get('lang')))

  if (frmu.feedbackMsg!=''):
    feedback = '''
      <div id="ZMSFormulatorFeedback" class="modal fade ZMSFormulatorFeedback-modal-lg" tabindex="-1" role="dialog" aria-labelledby="ZMSFormulatorFeedback" aria-hidden="true">
        <div class="modal-dialog modal-lg">
           <div class="modal-content" style="padding:1em;">%s</div>
        </div>
      </div>
    '''%(frmu.feedbackMsg.replace('\n','<br />'))
  else:
    feedback = '''
      <div id="ZMSFormulatorFeedback" class="modal fade ZMSFormulatorFeedback-modal-lg" tabindex="-1" role="dialog" aria-labelledby="ZMSFormulatorFeedback" aria-hidden="true">
        <div class="modal-dialog modal-lg">
          <div class="modal-content" style="padding:1em;">%s</div>
        </div>
      </div>
      '''%(self.getLangStr('ZMSFORMULATOR_FEEDBACK_MSG',self.REQUEST.get('lang')).replace('\n','<br />'))

  self.REQUEST.RESPONSE.setHeader('Cache-Control', 'no-cache')
  self.REQUEST.RESPONSE.setHeader('Pragma', 'no-cache')
  return output + jsed.render(frmu) + feedback